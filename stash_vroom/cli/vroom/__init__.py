#!/usr/bin/env python3
"""vroom - Stash database explorer

A CLI tool to interface with the Stash (AKA StashApp) media organizer.
`vroom` exposes the Stash GraphQL API, for queries and exploration.
"""

import argparse
import importlib.resources
import json
import os
import signal
import string
import sys
import httpx


import stash_vroom.stash

DEFAULT_STASH_SERVER = f'http://localhost:9999'
DEFAULT_STASH_ENDPOINT = f'{DEFAULT_STASH_SERVER}/graphql'

def _read_doc(name, context=None):
    """Read a bundled text file from this package, with $variable substitution."""
    text = importlib.resources.files(__package__).joinpath(name).read_text(encoding='utf-8')

    if not context:
        context = _default_docs_context()

    text = string.Template(text).safe_substitute(context)
    return text


def _default_docs_context():
    """Build template context for bundled docs."""
    result = {}

    stash_url = os.environ.get('STASH_URL')
    result['STASH_URL_STATUS'] = stash_url if stash_url else f'Unset, default is {DEFAULT_STASH_ENDPOINT}'

    stash_home = os.environ.get('STASH_HOME')
    result['STASH_HOME_STATUS'] = stash_home if stash_home else f'Unset, default is {stash_vroom.stash.STASH_HOME}'

    # Base URL for web UI links (GraphQL endpoint minus /graphql suffix)
    gql_url = stash_url or DEFAULT_STASH_ENDPOINT
    result['STASH_BASE_URL'] = gql_url.removesuffix('/graphql')

    api_key = os.environ.get('STASH_API_KEY')
    if api_key:
        result['STASH_API_KEY_STATUS'] = 'Set'
    else:
        api_key = stash_vroom.stash.get_api_key()
        if api_key:
            result['STASH_API_KEY_STATUS'] = f'Unset, using {stash_vroom.stash.STASH_HOME}/config.yml'
        else:
            result['STASH_API_KEY_STATUS'] = f'Unset and no config found!'

    return result


# ---------------------------------------------------------------------------
# Introspection query constants
# ---------------------------------------------------------------------------

INTROSPECT_TYPES_LIST = """
{
  __schema {
    types {
      name
      kind
      description
    }
  }
}
"""

INTROSPECT_TYPE_DETAIL = """
query IntrospectType($name: String!) {
  __type(name: $name) {
    name
    kind
    description
    fields {
      name
      description
      type { ...TypeRef }
      args {
        name
        type { ...TypeRef }
        defaultValue
      }
    }
    inputFields {
      name
      description
      type { ...TypeRef }
      defaultValue
    }
    enumValues {
      name
      description
    }
  }
}

fragment TypeRef on __Type {
  name kind
  ofType {
    name kind
    ofType {
      name kind
      ofType {
        name kind
        ofType { name kind }
      }
    }
  }
}
"""

# Full introspection for search (single round trip)
INTROSPECT_FULL = """
{
  __schema {
    types {
      name
      kind
      description
      fields {
        name
        description
        type {
          name kind
          ofType { name kind ofType { name kind ofType { name kind } } }
        }
      }
      inputFields {
        name
        description
        type {
          name kind
          ofType { name kind ofType { name kind ofType { name kind } } }
        }
      }
      enumValues {
        name
        description
      }
    }
  }
}
"""

INTROSPECT_ROOT = """
{
  __schema {
    queryType { name }
    mutationType { name }
  }
}
"""


# ---------------------------------------------------------------------------
# Connection and GraphQL helpers
# ---------------------------------------------------------------------------

def get_connection(args):
    """Return (url, headers) for Stash API."""
    url = getattr(args, 'url', None) or os.environ.get('STASH_URL', DEFAULT_STASH_ENDPOINT)
    api_key = stash_vroom.stash.get_api_key()
    headers = {'ApiKey': api_key, 'Content-Type': 'application/json'}
    return url, headers


def gql(url, headers, query, variables=None):
    """Execute a GraphQL query and return the data dict."""
    payload = {'query': query}
    if variables:
        payload['variables'] = variables
    resp = httpx.post(url, json=payload, headers=headers, timeout=30)
    try:
        body = resp.json()
    except Exception:
        resp.raise_for_status()
        raise
    if 'errors' in body:
        for err in body['errors']:
            print(f"GraphQL error: {err.get('message', err)}", file=sys.stderr)
        if 'data' not in body or body['data'] is None:
            sys.exit(1)
    if not resp.is_success:
        print(f"HTTP {resp.status_code}", file=sys.stderr)
        sys.exit(1)
    return body.get('data')


def render_type_ref(t):
    """Render a GraphQL type reference like [Scene!]! from introspection."""
    if t is None:
        return '?'
    kind = t.get('kind')
    if kind == 'NON_NULL':
        return f'{render_type_ref(t.get("ofType"))}!'
    if kind == 'LIST':
        return f'[{render_type_ref(t.get("ofType"))}]'
    return t.get('name') or '?'


def format_columns(rows, sep=';'):
    """Format rows into aligned columns separated by a delimiter.

    Each row is a list of values. Trailing None/empty values are omitted
    along with their separator, so no trailing whitespace or delimiters appear.
    Columns are right-padded only when a subsequent column exists on that row.
    """
    # Determine max width per column (only counting rows that have content beyond that column)
    col_count = max((len(r) for r in rows), default=0)
    max_widths = [0] * col_count
    for row in rows:
        # Find last non-empty column in this row
        last = len(row) - 1
        while last >= 0 and not row[last]:
            last -= 1
        # Only columns before `last` need padding
        for i in range(last):
            max_widths[i] = max(max_widths[i], len(str(row[i])))

    lines = []
    for row in rows:
        # Find last non-empty column
        last = len(row) - 1
        while last >= 0 and not row[last]:
            last -= 1
        if last < 0:
            lines.append('')
            continue
        parts = []
        for i in range(last + 1):
            val = str(row[i]) if i < len(row) else ''
            if i < last:
                parts.append(f'{val:<{max_widths[i]}}')
            else:
                parts.append(val)
        lines.append(f' {sep} '.join(parts))
    return '\n'.join(lines)


def strip_nulls(obj):
    """Remove null values from a dict/list tree for compact output."""
    if isinstance(obj, dict):
        return {k: strip_nulls(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [strip_nulls(v) for v in obj]
    return obj


def json_out(data, compact=False):
    """Print JSON, optionally compact (no nulls)."""
    if compact:
        data = strip_nulls(data)
    print(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# Command: logs
# ---------------------------------------------------------------------------

def cmd_logs(args):
    url, headers = get_connection(args)
    data = gql(url, headers, '{ logs { time level message } }')
    entries = data.get('logs') or []

    rows = []
    for e in entries:
        rows.append([e['level'], e['time'], e['message']])
    print(format_columns(rows))


# ---------------------------------------------------------------------------
# Command: version
# ---------------------------------------------------------------------------

def cmd_version(args):
    url, headers = get_connection(args)
    data = gql(url, headers, '{ version { version hash build_time } }')
    v = data['version']
    print(f"Stash {v['version']} (build {v['build_time']}, hash {v['hash'][:8]})")
    print(f"Endpoint: {url}")


# ---------------------------------------------------------------------------
# Command: config
# ---------------------------------------------------------------------------

def cmd_config(args):
    url, headers = get_connection(args)
    query = """
    {
      configuration {
        general {
          stashes { path excludeVideo excludeImage }
          databasePath
          generatedPath
          metadataPath
          cachePath
          calculateMD5
          videoFileNamingAlgorithm
          parallelTasks
          previewSegments
          previewSegmentDuration
          previewExcludeStart
          previewExcludeEnd
          previewPreset
          maxTranscodeSize
          maxStreamingTranscodeSize
          apiKey
          username
          ffmpegPath
          ffprobePath
          logLevel
          logAccess
          logOut
          stashBoxes { name endpoint }
        }
        defaults {
          scan {
            scanGenerateCovers
            scanGeneratePreviews
            scanGenerateImagePreviews
            scanGenerateSprites
            scanGeneratePhashes
            scanGenerateThumbnails
          }
        }
      }
    }
    """
    data = gql(url, headers, query)
    config = data['configuration']

    # Redact secrets
    general = config.get('general', {})
    if general.get('apiKey'):
        general['apiKey'] = '***'

    json_out(config, compact=True)


# ---------------------------------------------------------------------------
# Command: stats
# ---------------------------------------------------------------------------

def cmd_stats(args):
    url, headers = get_connection(args)
    query = """
    {
      findScenes(filter:{per_page:0}) { count }
      findImages(filter:{per_page:0}) { count }
      findPerformers(filter:{per_page:0}) { count }
      findStudios(filter:{per_page:0}) { count }
      findTags(filter:{per_page:0}) { count }
      findSceneMarkers(filter:{per_page:0}) { count }
      findGalleries(filter:{per_page:0}) { count }
    }
    """
    data = gql(url, headers, query)
    stats = [
        ('Scenes',     data['findScenes']['count']),
        ('Images',     data['findImages']['count']),
        ('Performers', data['findPerformers']['count']),
        ('Studios',    data['findStudios']['count']),
        ('Tags',       data['findTags']['count']),
        ('Markers',    data['findSceneMarkers']['count']),
        ('Galleries',  data['findGalleries']['count']),
    ]
    w = max(len(s[0]) for s in stats)
    for name, count in stats:
        print(f"  {name:<{w}}  {count:>8,}")


# ---------------------------------------------------------------------------
# Command: query
# ---------------------------------------------------------------------------

def cmd_gql(args):
    url, headers = get_connection(args)

    if args.file:
        if args.file == '-':
            query_str = sys.stdin.read()
        else:
            with open(args.file) as f:
                query_str = f.read()
    elif args.query:
        query_str = args.query
    elif not sys.stdin.isatty():
        query_str = sys.stdin.read()
    else:
        print("Provide a GraphQL query string, -f FILE, or pipe to stdin", file=sys.stderr)
        sys.exit(1)

    variables = None
    if args.variables:
        variables = json.loads(args.variables)

    data = gql(url, headers, query_str, variables)
    json_out(data, compact=True)




# ---------------------------------------------------------------------------
# Command: filters
# ---------------------------------------------------------------------------

FILTER_MODES = [
    'SCENES', 'IMAGES', 'PERFORMERS', 'STUDIOS',
    'TAGS', 'SCENE_MARKERS', 'GALLERIES', 'MOVIES', 'GROUPS',
]


def _resolve_filter_mode(args):
    """Resolve and validate filter mode from args."""
    mode = args.mode.upper()
    if mode not in FILTER_MODES:
        print(f"Invalid mode: {mode}", file=sys.stderr)
        print(f"Valid modes: {', '.join(m.lower() for m in FILTER_MODES)}", file=sys.stderr)
        sys.exit(1)
    return mode


def cmd_intro(args):
    topic = args.topic
    if not topic:
        print(_read_doc('help.md'), end='')
        return
    topics = {
        'queries': 'intro/queries.md',
        'discovery': 'intro/discovery.md',
        'filters': 'intro/filters.md',
        'mutations': 'intro/mutations.md',
        'ui-urls': 'intro/ui-urls.md',
        'ui-settings': 'intro/ui-settings.md',
    }
    if topic not in topics:
        print(f"Unknown topic: {topic}", file=sys.stderr)
        print(f"Available topics: {', '.join(topics)}", file=sys.stderr)
        sys.exit(1)
    print(_read_doc(topics[topic]), end='')


def cmd_filters(args):
    url, headers = get_connection(args)

    query = """
    query($mode: FilterMode!) {
      findSavedFilters(mode: $mode) {
        id mode name
      }
    }
    """
    rows = []
    for mode in FILTER_MODES:
        data = gql(url, headers, query, {'mode': mode})
        for f in data['findSavedFilters']:
            rows.append([mode, str(f['id']), f['name']])

    print(format_columns(rows))


# ---------------------------------------------------------------------------
# Command: filter (show or run)
# ---------------------------------------------------------------------------

def _fetch_default_filter(url, headers, mode):
    """Fetch the default filter for a mode from the UI config blob."""
    data = gql(url, headers, '{ configuration { ui } }')
    ui = data.get('configuration', {}).get('ui') or {}
    defaults = ui.get('defaultFilters') or {}
    key = mode.lower()
    found = defaults.get(key)
    if not found:
        print(f"No default filter for mode: {key}", file=sys.stderr)
        sys.exit(1)
    return found


def cmd_filter(args):
    url, headers = get_connection(args)
    mode = _resolve_filter_mode(args)

    if getattr(args, 'default', False):
        found = _fetch_default_filter(url, headers, mode)
    else:
        name_or_id = args.name
        if not name_or_id:
            print("Provide a filter name/ID, or use --default", file=sys.stderr)
            sys.exit(1)

        query = """
        query($mode: FilterMode!) {
          findSavedFilters(mode: $mode) {
            id mode name
            find_filter { q page per_page sort direction }
            object_filter
          }
        }
        """
        data = gql(url, headers, query, {'mode': mode})
        found = None
        for f in data['findSavedFilters']:
            if str(f['id']) == str(name_or_id) or f['name'].lower() == name_or_id.lower():
                found = f
                break

        if not found:
            print(f"Filter not found in {mode}: {name_or_id}", file=sys.stderr)
            sys.exit(1)

    # Show as GQL-ready syntax
    find_filter = found.get('find_filter') or {}
    object_filter = found.get('object_filter') or {}

    # Clean find_filter
    find_filter = {k: v for k, v in find_filter.items() if v is not None}

    # Convert UI filter format to GraphQL input format
    object_filter = convert_ui_filter(object_filter)

    query_name, filter_arg = MODE_QUERY_MAP[mode]

    if getattr(args, 'default', False):
        print(f"# Default filter for {mode}")
    else:
        print(f"# Saved filter {mode} id={found['id']}: {json.dumps(found['name'])}")
    print(f"#")

    # Build the GQL query string
    filter_json = json.dumps(find_filter, separators=(',', ':'))
    obj_filter_json = json.dumps(object_filter, indent=2)

    print(f"{{")
    print(f"  {query_name}(")
    print(f"    filter: {filter_json}")
    print(f"    {filter_arg}: {obj_filter_json}")
    print(f"  ) {{")
    print(f"    count")
    print(f"    # Add fields here, e.g.:")
    print(f"    # {_example_fields(mode)}")
    print(f"  }}")
    print(f"}}")


# Map mode → (queryName, filterArgName)
MODE_QUERY_MAP = {
    'SCENES':        ('findScenes',       'scene_filter'),
    'IMAGES':        ('findImages',       'image_filter'),
    'PERFORMERS':    ('findPerformers',   'performer_filter'),
    'STUDIOS':       ('findStudios',      'studio_filter'),
    'TAGS':          ('findTags',         'tag_filter'),
    'SCENE_MARKERS': ('findSceneMarkers', 'scene_marker_filter'),
    'GALLERIES':     ('findGalleries',    'gallery_filter'),
    'MOVIES':        ('findGroups',       'group_filter'),
    'GROUPS':        ('findGroups',       'group_filter'),
}


def _example_fields(mode):
    """Return example field selection for a mode."""
    examples = {
        'SCENES':        'scenes { id title rating100 date studio { name } performers { name } }',
        'IMAGES':        'images { id title tags { name } }',
        'PERFORMERS':    'performers { id name gender favorite }',
        'STUDIOS':       'studios { id name }',
        'TAGS':          'tags { id name }',
        'SCENE_MARKERS': 'scene_markers { id seconds scene { id title } primary_tag { name } }',
        'GALLERIES':     'galleries { id title }',
    }
    return examples.get(mode, '...')


def convert_ui_filter(flt):
    """Convert Stash UI saved filter format to GraphQL input format.

    The Stash UI stores filters in its own internal representation which
    differs from the GraphQL API input types. This function transforms
    the UI format to valid GraphQL input.

    Based on companion project's fix_filter() with additional patterns.
    """
    if not isinstance(flt, dict):
        return flt

    flt = dict(flt)  # shallow copy

    # HierarchicalMultiCriterionInput fields
    # UI: {modifier, value: {depth, items: [{id, label}], excluded: [{id, label}]}}
    # GQL: {modifier, value: [id...], excludes: [id...], depth}
    hierarchical_fields = [
        'tags', 'performer_tags', 'scene_tags', 'studios',
        'parent_tags', 'child_tags', 'parent_studios',
    ]
    for key in hierarchical_fields:
        if key not in flt:
            continue
        orig = flt[key]
        val = orig.get('value', {})
        if not isinstance(val, dict) or ('items' not in val and 'excluded' not in val):
            continue
        result = {'modifier': orig['modifier']}
        result['value'] = [x['id'] for x in val.get('items', [])]
        excluded = val.get('excluded', [])
        if excluded:
            result['excludes'] = [x['id'] for x in excluded]
        if 'depth' in val:
            result['depth'] = _to_int(val['depth'])
        flt[key] = result

    # MultiCriterionInput fields (no depth)
    # UI: {modifier, value: {items: [{id, label}], excluded: [{id, label}]}}
    # GQL: {modifier, value: [id...], excludes: [id...]}
    for key in ['performers', 'galleries', 'groups', 'movies', 'scenes',
                 'containing_groups', 'sub_groups']:
        if key not in flt:
            continue
        orig = flt[key]
        val = orig.get('value', {})
        if not isinstance(val, dict) or ('items' not in val and 'excluded' not in val):
            continue
        result = {'modifier': orig['modifier']}
        result['value'] = [x['id'] for x in val.get('items', [])]
        excluded = val.get('excluded', [])
        if excluded:
            result['excludes'] = [x['id'] for x in excluded]
        flt[key] = result

    # IntCriterionInput fields: {modifier, value: {value: N, value2: M}} -> {modifier, value: N}
    int_fields = [
        'file_count', 'performer_count', 'rating100', 'o_counter',
        'play_count', 'resume_time', 'play_duration', 'duration',
        'tag_count', 'image_count', 'gallery_count', 'performer_age',
        'interactive_speed', 'framerate', 'bitrate', 'weight',
        'scene_count', 'marker_count',
        'height_cm', 'birth_year', 'death_year', 'age', 'penis_length',
        'zip_file_count', 'containing_group_count', 'sub_group_count',
    ]
    for key in int_fields:
        if key not in flt:
            continue
        val = flt[key].get('value')
        if isinstance(val, dict) and 'value' in val:
            flt[key]['value'] = _to_int(val['value'])
            if 'value2' in val and val['value2'] is not None:
                flt[key]['value2'] = _to_int(val['value2'])
        elif isinstance(val, str):
            flt[key]['value'] = _to_int(val)

    # String-as-boolean fields: UI stores {modifier: "EQUALS", value: "true"} -> plain string
    for key in ['is_missing', 'has_markers', 'has_chapters']:
        if key in flt and isinstance(flt[key], dict):
            if flt[key].get('modifier') == 'EQUALS':
                flt[key] = flt[key]['value']

    # Boolean fields: UI stores {modifier: "EQUALS", value: "true"} -> plain bool
    for key in ['organized', 'performer_favorite', 'interactive',
                'favourite', 'ignore_auto_tag']:
        if key in flt and isinstance(flt[key], dict):
            if flt[key].get('modifier') == 'EQUALS':
                flt[key] = flt[key]['value'] in ('true', True)

    # DateCriterionInput fields: {modifier, value: {value: "2024-01-01", value2: "..."}}
    # -> {modifier, value: "2024-01-01", value2: "..."} (flatten nested, drop empty value2)
    date_fields = ['date', 'birthdate', 'death_date', 'scene_date']
    for key in date_fields:
        if key not in flt:
            continue
        val = flt[key].get('value')
        if isinstance(val, dict) and 'value' in val:
            flt[key]['value'] = val['value']
            if val.get('value2'):
                flt[key]['value2'] = val['value2']

    # TimestampCriterionInput fields: same nesting as date, plus normalize
    # space-separated datetime to ISO 8601 (T separator)
    timestamp_fields = ['created_at', 'updated_at', 'last_played_at',
                        'scene_created_at', 'scene_updated_at']
    for key in timestamp_fields:
        if key not in flt:
            continue
        val = flt[key].get('value')
        if isinstance(val, dict) and 'value' in val:
            flt[key]['value'] = _normalize_timestamp(val['value'])
            if val.get('value2'):
                flt[key]['value2'] = _normalize_timestamp(val['value2'])

    # StashIdCriterionInput: {modifier, value: {endpoint, stashID}}
    # -> {modifier, endpoint, stash_id}
    if 'stash_id_endpoint' in flt:
        orig = flt['stash_id_endpoint']
        val = orig.get('value', {})
        if isinstance(val, dict) and 'stashID' in val:
            flt['stash_id_endpoint'] = {
                'modifier': orig['modifier'],
                'endpoint': val.get('endpoint', ''),
                'stash_id': val['stashID'],
            }

    # PhashDistanceCriterionInput: {modifier, value: {value: "hash", distance: N}}
    # -> {modifier, value: "hash", distance: N}
    if 'phash_distance' in flt:
        orig = flt['phash_distance']
        val = orig.get('value')
        if isinstance(val, dict) and 'distance' in val:
            flt['phash_distance'] = {
                'modifier': orig['modifier'],
                'value': val['value'],
                'distance': _to_int(val['distance']),
            }

    # PHashDuplicationCriterionInput: {modifier, value: "true"/"false"}
    # -> {duplicated: bool}
    if 'duplicated_phash' in flt:
        orig = flt['duplicated_phash']
        if isinstance(orig, dict) and 'value' in orig:
            flt['duplicated_phash'] = {
                'duplicated': orig['value'] in ('true', True),
            }

    # OrientationCriterionInput: {modifier, value: [enum...]}
    # -> {value: [enum...]}  (modifier stripped)
    if 'orientation' in flt:
        orig = flt['orientation']
        if isinstance(orig, dict) and isinstance(orig.get('value'), list):
            flt['orientation'] = {'value': orig['value']}

    # GenderCriterionInput: {modifier, value: [enum...] | "enum"}
    # -> {modifier, value_list: [enum...]}  (field rename + legacy single-string)
    if 'gender' in flt:
        orig = flt['gender']
        if isinstance(orig, dict):
            val = orig.get('value')
            if isinstance(val, str):
                val = [val]
            flt['gender'] = {'modifier': orig['modifier'], 'value_list': val}

    return flt


def _normalize_timestamp(val):
    """Normalize space-separated datetime to ISO 8601 T separator."""
    if isinstance(val, str) and ' ' in val:
        return val.replace(' ', 'T', 1)
    return val


def _to_int(val):
    """Coerce string-encoded integers from UI format to int."""
    if isinstance(val, str):
        try:
            return int(val)
        except ValueError:
            return val
    return val


# ---------------------------------------------------------------------------
# Command: schema intro
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Command: schema types
# ---------------------------------------------------------------------------

def cmd_schema_types(args):
    url, headers = get_connection(args)
    data = gql(url, headers, INTROSPECT_TYPES_LIST)
    types = data['__schema']['types']

    # Skip introspection types
    types = [t for t in types if not t['name'].startswith('__')]
    types.sort(key=lambda t: (t['kind'], t['name']))

    rows = []
    for t in types:
        desc = None
        if t.get('description'):
            desc = t['description'].split('\n')[0].split('.')[0].strip()
            if len(desc) > 60:
                desc = desc[:57] + '...'
        rows.append([t['kind'], t['name'], desc])
    print(format_columns(rows))


# ---------------------------------------------------------------------------
# Command: schema type <name>
# ---------------------------------------------------------------------------

def cmd_schema_type(args):
    names = args.names
    is_multi = getattr(args, 'multi', False)

    if len(names) > 1 and not is_multi:
        print("INFO: Multiple types passed; enabling --multi mode", file=sys.stderr)
        is_multi = True

    url, headers = get_connection(args)

    for name in names:
        _print_type(url, headers, name, is_multi)


def _print_type(url, headers, name, is_multi):
    data = gql(url, headers, INTROSPECT_TYPE_DETAIL, {'name': name})
    t = data['__type']

    if not t:
        print(f"Type not found: {name}", file=sys.stderr)
        sys.exit(1)

    if is_multi:
        print(t['name'])
        print('-' * len(t['name']))

    if t.get('fields'):
        rows = []
        for f in t['fields']:
            type_str = render_type_ref(f['type'])
            fname = f['name']
            if f.get('args'):
                arg_parts = []
                for a in f['args']:
                    a_str = f"{a['name']}: {render_type_ref(a['type'])}"
                    if a.get('defaultValue'):
                        a_str += f" = {a['defaultValue']}"
                    arg_parts.append(a_str)
                fname = f"{fname}({', '.join(arg_parts)})"
            rows.append([fname, type_str, f.get('description')])
        print(format_columns(rows))

    if t.get('inputFields'):
        rows = []
        for f in t['inputFields']:
            type_str = render_type_ref(f['type'])
            if f.get('defaultValue'):
                type_str += f" = {f['defaultValue']}"
            desc = f.get('description')
            rows.append([f['name'], type_str, desc])
        print(format_columns(rows))

    if t.get('enumValues'):
        rows = []
        for v in t['enumValues']:
            rows.append([v['name'], v.get('description')])
        print(format_columns(rows))

    if is_multi:
        print()


# ---------------------------------------------------------------------------
# Command: schema queries / schema mutations
# ---------------------------------------------------------------------------

def _print_root_type_fields(args, kind_label):
    url, headers = get_connection(args)
    root_data = gql(url, headers, INTROSPECT_ROOT)

    key = 'queryType' if kind_label == 'Queries' else 'mutationType'
    root_type = root_data['__schema'].get(key)
    if not root_type or not root_type.get('name'):
        print(f"No {kind_label.lower()} type found")
        return

    data = gql(url, headers, INTROSPECT_TYPE_DETAIL, {'name': root_type['name']})
    t = data['__type']

    for f in sorted(t['fields'], key=lambda x: x['name']):
        ret_type = render_type_ref(f['type'])
        if f.get('args'):
            arg_strs = [f"{a['name']}: {render_type_ref(a['type'])}" for a in f['args']]
            print(f"{f['name']}({', '.join(arg_strs)}): {ret_type}")
        else:
            print(f"{f['name']}: {ret_type}")


def cmd_schema_queries(args):
    _print_root_type_fields(args, 'Queries')


def cmd_schema_mutations(args):
    _print_root_type_fields(args, 'Mutations')


# ---------------------------------------------------------------------------
# Command: schema search
# ---------------------------------------------------------------------------

def cmd_schema_search(args):
    url, headers = get_connection(args)
    term = args.term.lower()

    # Single round trip: fetch all types with fields
    data = gql(url, headers, INTROSPECT_FULL)
    all_types = [t for t in data['__schema']['types'] if not t['name'].startswith('__')]

    # Search type names
    type_matches = [t for t in all_types if term in t['name'].lower()
                    or (t.get('description') and term in t['description'].lower())]

    if type_matches:
        print(f"Types matching '{args.term}':")
        for t in sorted(type_matches, key=lambda x: x['name']):
            desc = ''
            if t.get('description'):
                first = t['description'].split('\n')[0].split('.')[0].strip()
                if len(first) > 60:
                    first = first[:57] + '...'
                desc = f'  {first}'
            print(f"  {t['kind']:<14} {t['name']}{desc}")

    # Search field names
    field_matches = []
    for t in all_types:
        fields = t.get('fields') or t.get('inputFields') or []
        for f in fields:
            if term in f['name'].lower() or (f.get('description') and term in f['description'].lower()):
                field_matches.append((t['name'], f['name'], render_type_ref(f['type'])))

    if field_matches:
        if type_matches:
            print()
        print(f"Fields matching '{args.term}':")
        for type_name, field_name, field_type in sorted(field_matches):
            print(f"  {type_name}.{field_name}: {field_type}")

    # Search enum values
    enum_matches = []
    for t in all_types:
        if t.get('enumValues'):
            for v in t['enumValues']:
                if term in v['name'].lower():
                    enum_matches.append((t['name'], v['name']))

    if enum_matches:
        if type_matches or field_matches:
            print()
        print(f"Enum values matching '{args.term}':")
        for type_name, value_name in sorted(enum_matches):
            print(f"  {type_name}.{value_name}")

    if not type_matches and not field_matches and not enum_matches:
        print(f"No matches for '{args.term}'")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog='vroom',
        description=__doc__, # This file's docstring
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_read_doc('help.md'),
    )
    #parser._optionals.title = 'Options'
    parser._optionals.title = 'Universal Options'
    parser._optionals.title += ' (rarely needed)'

    parser.add_argument('--url', help=f'Stash GraphQL endpoint; default: {DEFAULT_STASH_ENDPOINT}')

    sub = parser.add_subparsers(dest='command')

    # Remove the auto-generated subcommand group from --help output.
    # The help.md epilog has a better-formatted command list.
    parser._subparsers._group_actions.clear()

    sub.add_parser('version')
    sub.add_parser('config')
    sub.add_parser('stats')

    sub.add_parser('logs',
        description='Greppable list of recent log entries (~30 cached by the server).')

    p_intro = sub.add_parser('intro',
        description='Read introductory guides on a topic.')
    p_intro.add_argument('topic', nargs='?', default=None, help='Topic: queries, discovery, filters, mutations, ui-urls, ui-settings')

    p_query = sub.add_parser('gql',
        description='Execute an arbitrary GraphQL query and print the result as JSON.',
        epilog="Reads from stdin if no query or -f given. Use -f - for explicit stdin.")
    p_query.add_argument('query', nargs='?', help='GraphQL query string')
    p_query.add_argument('-f', '--file', help='Read query from file (use - for stdin)')
    p_query.add_argument('-v', '--variables', help='JSON string of query variables')

    sub.add_parser('filters',
        description='Greppable list of all saved filters across all modes.')

    p_filter = sub.add_parser('filter',
        description='Display a saved filter converted to GraphQL query syntax, ready to copy/modify.')
    p_filter.add_argument('mode', help='Filter mode: ' + ', '.join(m.lower() for m in FILTER_MODES))
    p_filter.add_argument('name', nargs='?', default=None, help='Filter name or ID')
    p_filter.add_argument('--default', action='store_true', help='Show the default filter for this mode')

    p_schema = sub.add_parser('schema',
        description='Discover types, fields, queries, and mutations in the Stash GraphQL API.')
    schema_sub = p_schema.add_subparsers(dest='schema_command')

    schema_sub.add_parser('types',
        help='Greppable list of all types (pipe to grep to search)')

    p_type = schema_sub.add_parser('type',
        help='Show all fields for a named type')
    p_type.add_argument('names', nargs='+', help='Type name(s) (e.g. Scene, SceneFilterType, CriterionModifier)')
    p_type.add_argument('--multi', action='store_true', help='Prefix with type name, suffix with blank line')

    schema_sub.add_parser('queries',
        help='List all query operations with argument signatures')

    schema_sub.add_parser('mutations',
        help='List all mutation operations with signatures')

    p_search = schema_sub.add_parser('search',
        help='Search type names, field names, and enum values')
    p_search.add_argument('term', help='Search term (case-insensitive)')

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    # Let piping to head/grep etc. exit cleanly instead of BrokenPipeError.
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    dispatch = {
        'version': cmd_version,
        'config': cmd_config,
        'stats': cmd_stats,
        'gql': cmd_gql,
        'filters': cmd_filters,
        'filter': cmd_filter,
        'intro': cmd_intro,
        'logs': cmd_logs,
    }

    if args.command in dispatch:
        try:
            dispatch[args.command](args)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    if args.command == 'schema':
        schema_dispatch = {
            'types': cmd_schema_types,
            'type': cmd_schema_type,
            'queries': cmd_schema_queries,
            'mutations': cmd_schema_mutations,
            'search': cmd_schema_search,
        }
        schema_cmd = getattr(args, 'schema_command', None)
        if not schema_cmd:
            parser.parse_args(['schema', '--help'])
            return
        if schema_cmd in schema_dispatch:
            try:
                schema_dispatch[schema_cmd](args)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
            return

    parser.print_help()

if __name__ == '__main__':
    main()
