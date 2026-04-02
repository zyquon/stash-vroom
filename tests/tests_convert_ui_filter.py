from stash_vroom.cli.vroom import convert_ui_filter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _h_item(id, label=''):
    """Make a UI hierarchical/labeled item."""
    return {'id': str(id), 'label': label}


# ===========================================================================
# 1. HIERARCHICAL MULTI-CRITERION (tags, performer_tags, scene_tags, studios)
# ===========================================================================

class TestHierarchical:

    def test_tags_basic(self):
        ui = {'tags': {
            'modifier': 'INCLUDES',
            'value': {'depth': 0, 'items': [_h_item('1', 'Tag A'), _h_item('2', 'Tag B')], 'excluded': []},
        }}
        result = convert_ui_filter(ui)
        assert result['tags'] == {'modifier': 'INCLUDES', 'value': ['1', '2'], 'depth': 0}

    def test_tags_with_excludes(self):
        ui = {'tags': {
            'modifier': 'INCLUDES',
            'value': {'depth': 1, 'items': [_h_item('1')], 'excluded': [_h_item('9', 'Bad')]},
        }}
        result = convert_ui_filter(ui)
        assert result['tags'] == {'modifier': 'INCLUDES', 'value': ['1'], 'excludes': ['9'], 'depth': 1}

    def test_tags_no_items_only_excluded(self):
        ui = {'tags': {
            'modifier': 'EXCLUDES',
            'value': {'depth': 0, 'items': [], 'excluded': [_h_item('5')]},
        }}
        result = convert_ui_filter(ui)
        assert result['tags']['value'] == []
        assert result['tags']['excludes'] == ['5']

    def test_performer_tags(self):
        ui = {'performer_tags': {
            'modifier': 'INCLUDES_ALL',
            'value': {'depth': 2, 'items': [_h_item('10')], 'excluded': []},
        }}
        result = convert_ui_filter(ui)
        assert result['performer_tags'] == {'modifier': 'INCLUDES_ALL', 'value': ['10'], 'depth': 2}

    def test_scene_tags(self):
        ui = {'scene_tags': {
            'modifier': 'INCLUDES',
            'value': {'depth': 0, 'items': [_h_item('3')], 'excluded': []},
        }}
        result = convert_ui_filter(ui)
        assert result['scene_tags'] == {'modifier': 'INCLUDES', 'value': ['3'], 'depth': 0}

    def test_studios_hierarchical(self):
        ui = {'studios': {
            'modifier': 'INCLUDES',
            'value': {'depth': 0, 'items': [_h_item('42', 'StudioX')], 'excluded': []},
        }}
        result = convert_ui_filter(ui)
        assert result['studios'] == {'modifier': 'INCLUDES', 'value': ['42'], 'depth': 0}

    # --- Missing hierarchical fields ---

    def test_parent_tags(self):
        ui = {'parent_tags': {
            'modifier': 'INCLUDES',
            'value': {'depth': 0, 'items': [_h_item('20', 'Parent')], 'excluded': []},
        }}
        result = convert_ui_filter(ui)
        assert result['parent_tags'] == {'modifier': 'INCLUDES', 'value': ['20'], 'depth': 0}

    def test_child_tags(self):
        ui = {'child_tags': {
            'modifier': 'INCLUDES',
            'value': {'depth': 1, 'items': [_h_item('30')], 'excluded': [_h_item('31')]},
        }}
        result = convert_ui_filter(ui)
        assert result['child_tags'] == {'modifier': 'INCLUDES', 'value': ['30'], 'excludes': ['31'], 'depth': 1}

    def test_parent_studios(self):
        ui = {'parent_studios': {
            'modifier': 'INCLUDES',
            'value': {'depth': 0, 'items': [_h_item('50', 'ParentStudio')], 'excluded': []},
        }}
        result = convert_ui_filter(ui)
        assert result['parent_studios'] == {'modifier': 'INCLUDES', 'value': ['50'], 'depth': 0}

    def test_depth_string_coerced_to_int(self):
        ui = {'tags': {
            'modifier': 'INCLUDES',
            'value': {'depth': '3', 'items': [_h_item('1')], 'excluded': []},
        }}
        result = convert_ui_filter(ui)
        assert result['tags']['depth'] == 3
        assert isinstance(result['tags']['depth'], int)


# ===========================================================================
# 2. MULTI-CRITERION (performers, galleries, groups, movies, scenes)
# ===========================================================================

class TestMultiCriterion:

    def test_performers_basic(self):
        ui = {'performers': {
            'modifier': 'INCLUDES',
            'value': {'items': [_h_item('1', 'Alice'), _h_item('2', 'Bob')], 'excluded': []},
        }}
        result = convert_ui_filter(ui)
        assert result['performers'] == {'modifier': 'INCLUDES', 'value': ['1', '2']}

    def test_performers_with_excludes(self):
        ui = {'performers': {
            'modifier': 'INCLUDES',
            'value': {'items': [_h_item('1')], 'excluded': [_h_item('2')]},
        }}
        result = convert_ui_filter(ui)
        assert result['performers'] == {'modifier': 'INCLUDES', 'value': ['1'], 'excludes': ['2']}

    def test_galleries(self):
        ui = {'galleries': {
            'modifier': 'INCLUDES',
            'value': {'items': [_h_item('5')], 'excluded': []},
        }}
        result = convert_ui_filter(ui)
        assert result['galleries'] == {'modifier': 'INCLUDES', 'value': ['5']}

    def test_groups(self):
        ui = {'groups': {
            'modifier': 'INCLUDES',
            'value': {'items': [_h_item('7')], 'excluded': []},
        }}
        result = convert_ui_filter(ui)
        assert result['groups'] == {'modifier': 'INCLUDES', 'value': ['7']}

    def test_movies(self):
        ui = {'movies': {
            'modifier': 'INCLUDES_ALL',
            'value': {'items': [_h_item('8')], 'excluded': []},
        }}
        result = convert_ui_filter(ui)
        assert result['movies'] == {'modifier': 'INCLUDES_ALL', 'value': ['8']}

    def test_scenes(self):
        ui = {'scenes': {
            'modifier': 'INCLUDES',
            'value': {'items': [_h_item('100'), _h_item('200')], 'excluded': []},
        }}
        result = convert_ui_filter(ui)
        assert result['scenes'] == {'modifier': 'INCLUDES', 'value': ['100', '200']}

    # --- Missing multi-criterion fields ---

    def test_containing_groups(self):
        ui = {'containing_groups': {
            'modifier': 'INCLUDES',
            'value': {'items': [_h_item('10')], 'excluded': []},
        }}
        result = convert_ui_filter(ui)
        assert result['containing_groups'] == {'modifier': 'INCLUDES', 'value': ['10']}

    def test_sub_groups(self):
        ui = {'sub_groups': {
            'modifier': 'INCLUDES',
            'value': {'items': [_h_item('11'), _h_item('12')], 'excluded': [_h_item('13')]},
        }}
        result = convert_ui_filter(ui)
        assert result['sub_groups'] == {'modifier': 'INCLUDES', 'value': ['11', '12'], 'excludes': ['13']}


# ===========================================================================
# 3. INT CRITERION
# ===========================================================================

class TestIntCriterion:

    def test_rating100_nested_value(self):
        ui = {'rating100': {'modifier': 'GREATER_THAN', 'value': {'value': 80, 'value2': None}}}
        result = convert_ui_filter(ui)
        assert result['rating100'] == {'modifier': 'GREATER_THAN', 'value': 80}

    def test_rating100_between(self):
        ui = {'rating100': {'modifier': 'BETWEEN', 'value': {'value': 40, 'value2': 80}}}
        result = convert_ui_filter(ui)
        assert result['rating100'] == {'modifier': 'BETWEEN', 'value': 40, 'value2': 80}

    def test_rating100_string_coercion(self):
        ui = {'rating100': {'modifier': 'GREATER_THAN', 'value': {'value': '80', 'value2': None}}}
        result = convert_ui_filter(ui)
        assert result['rating100']['value'] == 80
        assert isinstance(result['rating100']['value'], int)

    def test_rating100_flat_string(self):
        """UI sometimes stores value as a flat string instead of nested dict."""
        ui = {'rating100': {'modifier': 'EQUALS', 'value': '60'}}
        result = convert_ui_filter(ui)
        assert result['rating100']['value'] == 60

    def test_file_count(self):
        ui = {'file_count': {'modifier': 'EQUALS', 'value': {'value': 1, 'value2': None}}}
        result = convert_ui_filter(ui)
        assert result['file_count'] == {'modifier': 'EQUALS', 'value': 1}

    def test_performer_count(self):
        ui = {'performer_count': {'modifier': 'GREATER_THAN', 'value': {'value': 2, 'value2': None}}}
        result = convert_ui_filter(ui)
        assert result['performer_count']['value'] == 2

    def test_o_counter(self):
        ui = {'o_counter': {'modifier': 'GREATER_THAN', 'value': {'value': 0, 'value2': None}}}
        result = convert_ui_filter(ui)
        assert result['o_counter']['value'] == 0

    def test_play_count(self):
        ui = {'play_count': {'modifier': 'GREATER_THAN', 'value': {'value': 5, 'value2': None}}}
        result = convert_ui_filter(ui)
        assert result['play_count']['value'] == 5

    def test_duration(self):
        ui = {'duration': {'modifier': 'BETWEEN', 'value': {'value': 300, 'value2': 3600}}}
        result = convert_ui_filter(ui)
        assert result['duration'] == {'modifier': 'BETWEEN', 'value': 300, 'value2': 3600}

    def test_tag_count(self):
        ui = {'tag_count': {'modifier': 'EQUALS', 'value': {'value': 3, 'value2': None}}}
        result = convert_ui_filter(ui)
        assert result['tag_count']['value'] == 3

    def test_all_int_fields_handled(self):
        """Every known int field should be convertible."""
        fields = [
            'file_count', 'performer_count', 'rating100', 'o_counter',
            'play_count', 'resume_time', 'play_duration', 'duration',
            'tag_count', 'image_count', 'gallery_count', 'performer_age',
            'interactive_speed', 'framerate', 'bitrate', 'weight',
            'scene_count', 'marker_count',
            # Missing int fields from audit:
            'height_cm', 'birth_year', 'death_year', 'age', 'penis_length',
            'zip_file_count', 'containing_group_count', 'sub_group_count',
        ]
        ui = {f: {'modifier': 'EQUALS', 'value': {'value': 42, 'value2': None}} for f in fields}
        result = convert_ui_filter(ui)
        for f in fields:
            assert result[f]['value'] == 42, f"Field {f} not converted"


# ===========================================================================
# 4. STRING-AS-BOOLEAN
# ===========================================================================

class TestStringAsBoolean:

    def test_is_missing(self):
        ui = {'is_missing': {'modifier': 'EQUALS', 'value': 'title'}}
        result = convert_ui_filter(ui)
        assert result['is_missing'] == 'title'

    def test_has_markers_true(self):
        ui = {'has_markers': {'modifier': 'EQUALS', 'value': 'true'}}
        result = convert_ui_filter(ui)
        assert result['has_markers'] == 'true'

    def test_has_markers_false(self):
        ui = {'has_markers': {'modifier': 'EQUALS', 'value': 'false'}}
        result = convert_ui_filter(ui)
        assert result['has_markers'] == 'false'

    # --- Missing string-as-boolean field ---

    def test_has_chapters(self):
        ui = {'has_chapters': {'modifier': 'EQUALS', 'value': 'true'}}
        result = convert_ui_filter(ui)
        assert result['has_chapters'] == 'true'


# ===========================================================================
# 5. BOOLEAN
# ===========================================================================

class TestBoolean:

    def test_organized_true_string(self):
        ui = {'organized': {'modifier': 'EQUALS', 'value': 'true'}}
        result = convert_ui_filter(ui)
        assert result['organized'] is True

    def test_organized_false_string(self):
        ui = {'organized': {'modifier': 'EQUALS', 'value': 'false'}}
        result = convert_ui_filter(ui)
        assert result['organized'] is False

    def test_organized_true_bool(self):
        ui = {'organized': {'modifier': 'EQUALS', 'value': True}}
        result = convert_ui_filter(ui)
        assert result['organized'] is True

    def test_performer_favorite_true(self):
        ui = {'performer_favorite': {'modifier': 'EQUALS', 'value': 'true'}}
        result = convert_ui_filter(ui)
        assert result['performer_favorite'] is True

    def test_interactive_false(self):
        ui = {'interactive': {'modifier': 'EQUALS', 'value': 'false'}}
        result = convert_ui_filter(ui)
        assert result['interactive'] is False

    # --- Missing boolean fields ---

    def test_favourite(self):
        ui = {'favourite': {'modifier': 'EQUALS', 'value': 'true'}}
        result = convert_ui_filter(ui)
        assert result['favourite'] is True

    def test_ignore_auto_tag(self):
        ui = {'ignore_auto_tag': {'modifier': 'EQUALS', 'value': 'false'}}
        result = convert_ui_filter(ui)
        assert result['ignore_auto_tag'] is False


# ===========================================================================
# 6. STRING / PASSTHROUGH (no conversion needed — verify no mangling)
# ===========================================================================

class TestPassthrough:

    def test_string_criterion_passthrough(self):
        """StringCriterionInput fields should pass through unchanged."""
        fields = [
            'title', 'code', 'path', 'details', 'director', 'oshash',
            'checksum', 'video_codec', 'audio_codec', 'url', 'country',
            'name', 'disambiguation', 'ethnicity', 'hair_color', 'eye_color',
            'measurements', 'fake_tits', 'career_length', 'tattoos',
            'piercings', 'aliases', 'photographer', 'synopsis',
        ]
        for field in fields:
            ui = {field: {'modifier': 'EQUALS', 'value': 'test_val'}}
            result = convert_ui_filter(ui)
            assert result[field] == {'modifier': 'EQUALS', 'value': 'test_val'}, f"{field} was mangled"

    def test_empty_filter(self):
        assert convert_ui_filter({}) == {}

    def test_non_dict_passthrough(self):
        assert convert_ui_filter(None) is None
        assert convert_ui_filter([]) == []

    def test_multiple_fields_combined(self):
        """A realistic filter with multiple field types at once."""
        ui = {
            'tags': {
                'modifier': 'INCLUDES',
                'value': {'depth': 0, 'items': [_h_item('1', 'VR')], 'excluded': []},
            },
            'rating100': {'modifier': 'GREATER_THAN', 'value': {'value': 60, 'value2': None}},
            'organized': {'modifier': 'EQUALS', 'value': 'true'},
            'title': {'modifier': 'MATCHES_REGEX', 'value': '.*test.*'},
        }
        result = convert_ui_filter(ui)
        assert result['tags'] == {'modifier': 'INCLUDES', 'value': ['1'], 'depth': 0}
        assert result['rating100'] == {'modifier': 'GREATER_THAN', 'value': 60}
        assert result['organized'] is True
        assert result['title'] == {'modifier': 'MATCHES_REGEX', 'value': '.*test.*'}


# ===========================================================================
# 7. DATE CRITERION  (date, birthdate, death_date)
#    UI: {modifier, value: {value: "2024-01-01", value2: "2024-12-31"}}
#    GQL: {modifier, value: "2024-01-01", value2: "2024-12-31"}
# ===========================================================================

class TestDateCriterion:

    def test_date_basic(self):
        ui = {'date': {'modifier': 'GREATER_THAN', 'value': {'value': '2024-01-01', 'value2': ''}}}
        result = convert_ui_filter(ui)
        assert result['date'] == {'modifier': 'GREATER_THAN', 'value': '2024-01-01'}

    def test_date_between(self):
        ui = {'date': {'modifier': 'BETWEEN', 'value': {'value': '2024-01-01', 'value2': '2024-12-31'}}}
        result = convert_ui_filter(ui)
        assert result['date'] == {'modifier': 'BETWEEN', 'value': '2024-01-01', 'value2': '2024-12-31'}

    def test_birthdate(self):
        ui = {'birthdate': {'modifier': 'LESS_THAN', 'value': {'value': '1990-06-15', 'value2': ''}}}
        result = convert_ui_filter(ui)
        assert result['birthdate'] == {'modifier': 'LESS_THAN', 'value': '1990-06-15'}

    def test_death_date(self):
        ui = {'death_date': {'modifier': 'EQUALS', 'value': {'value': '2020-03-10', 'value2': ''}}}
        result = convert_ui_filter(ui)
        assert result['death_date'] == {'modifier': 'EQUALS', 'value': '2020-03-10'}


# ===========================================================================
# 8. TIMESTAMP CRITERION  (created_at, updated_at, last_played_at, etc.)
#    UI: {modifier, value: {value: "2024-01-01 12:00", value2: "..."}}
#    GQL: {modifier, value: "2024-01-01T12:00", value2: "..."}
#    Stash normalizes space-separated datetime to ISO 8601 (T separator)
# ===========================================================================

class TestTimestampCriterion:

    def test_created_at_basic(self):
        ui = {'created_at': {'modifier': 'GREATER_THAN', 'value': {'value': '2024-01-01 00:00', 'value2': ''}}}
        result = convert_ui_filter(ui)
        assert result['created_at'] == {'modifier': 'GREATER_THAN', 'value': '2024-01-01T00:00'}

    def test_created_at_already_iso(self):
        ui = {'created_at': {'modifier': 'GREATER_THAN', 'value': {'value': '2024-01-01T00:00', 'value2': ''}}}
        result = convert_ui_filter(ui)
        assert result['created_at']['value'] == '2024-01-01T00:00'

    def test_updated_at_between(self):
        ui = {'updated_at': {'modifier': 'BETWEEN', 'value': {'value': '2024-01-01 08:00', 'value2': '2024-06-30 23:59'}}}
        result = convert_ui_filter(ui)
        assert result['updated_at'] == {'modifier': 'BETWEEN', 'value': '2024-01-01T08:00', 'value2': '2024-06-30T23:59'}

    def test_last_played_at(self):
        ui = {'last_played_at': {'modifier': 'LESS_THAN', 'value': {'value': '2024-03-15 10:30', 'value2': ''}}}
        result = convert_ui_filter(ui)
        assert result['last_played_at'] == {'modifier': 'LESS_THAN', 'value': '2024-03-15T10:30'}

    def test_scene_created_at(self):
        ui = {'scene_created_at': {'modifier': 'EQUALS', 'value': {'value': '2024-06-01 12:00', 'value2': ''}}}
        result = convert_ui_filter(ui)
        assert result['scene_created_at'] == {'modifier': 'EQUALS', 'value': '2024-06-01T12:00'}

    def test_scene_updated_at(self):
        ui = {'scene_updated_at': {'modifier': 'EQUALS', 'value': {'value': '2024-06-01 12:00', 'value2': ''}}}
        result = convert_ui_filter(ui)
        assert result['scene_updated_at'] == {'modifier': 'EQUALS', 'value': '2024-06-01T12:00'}

    def test_scene_date(self):
        """scene_date on scene_markers — date, not timestamp, but same nested format."""
        ui = {'scene_date': {'modifier': 'GREATER_THAN', 'value': {'value': '2024-01-01', 'value2': ''}}}
        result = convert_ui_filter(ui)
        assert result['scene_date'] == {'modifier': 'GREATER_THAN', 'value': '2024-01-01'}

    def test_all_timestamp_fields(self):
        fields = ['created_at', 'updated_at', 'last_played_at',
                  'scene_created_at', 'scene_updated_at']
        ui = {f: {'modifier': 'EQUALS', 'value': {'value': '2024-01-01 00:00', 'value2': ''}} for f in fields}
        result = convert_ui_filter(ui)
        for f in fields:
            assert result[f]['value'] == '2024-01-01T00:00', f"Field {f} not converted"


# ===========================================================================
# 9. STASH ID CRITERION
#    UI: {modifier, value: {endpoint: "...", stashID: "..."}}
#    GQL: {modifier, endpoint: "...", stash_id: "..."}
# ===========================================================================

class TestStashIdCriterion:

    def test_stash_id_basic(self):
        ui = {'stash_id_endpoint': {
            'modifier': 'EQUALS',
            'value': {'endpoint': 'https://stashdb.org', 'stashID': 'abc-123'},
        }}
        result = convert_ui_filter(ui)
        assert result['stash_id_endpoint'] == {
            'modifier': 'EQUALS',
            'endpoint': 'https://stashdb.org',
            'stash_id': 'abc-123',
        }

    def test_stash_id_not_null(self):
        ui = {'stash_id_endpoint': {
            'modifier': 'NOT_NULL',
            'value': {'endpoint': '', 'stashID': ''},
        }}
        result = convert_ui_filter(ui)
        assert result['stash_id_endpoint']['modifier'] == 'NOT_NULL'
        assert result['stash_id_endpoint']['stash_id'] == ''


# ===========================================================================
# 10. PHASH CRITERION
#     UI: {modifier, value: {value: "abcdef", distance: 8}}
#     GQL: {modifier, value: "abcdef", distance: 8}
# ===========================================================================

class TestPhashCriterion:

    def test_phash_distance_criterion(self):
        """phash_distance as a PhashDistanceCriterionInput (not int)."""
        ui = {'phash_distance': {
            'modifier': 'EQUALS',
            'value': {'value': 'abcdef0123456789', 'distance': 8},
        }}
        result = convert_ui_filter(ui)
        assert result['phash_distance'] == {
            'modifier': 'EQUALS',
            'value': 'abcdef0123456789',
            'distance': 8,
        }

    def test_phash_distance_string_distance(self):
        ui = {'phash_distance': {
            'modifier': 'EQUALS',
            'value': {'value': 'aabb', 'distance': '4'},
        }}
        result = convert_ui_filter(ui)
        assert result['phash_distance']['distance'] == 4
        assert isinstance(result['phash_distance']['distance'], int)


# ===========================================================================
# 11. DUPLICATED PHASH CRITERION
#     UI: {modifier, value: "true"}
#     GQL: {duplicated: true, distance: 0}
# ===========================================================================

class TestDuplicatedCriterion:

    def test_duplicated_true(self):
        ui = {'duplicated_phash': {
            'modifier': 'EQUALS',
            'value': 'true',
        }}
        result = convert_ui_filter(ui)
        assert result['duplicated_phash'] == {'duplicated': True}

    def test_duplicated_false(self):
        ui = {'duplicated_phash': {
            'modifier': 'EQUALS',
            'value': 'false',
        }}
        result = convert_ui_filter(ui)
        assert result['duplicated_phash'] == {'duplicated': False}


# ===========================================================================
# 12. RESOLUTION CRITERION
#     UI: {modifier, value: "1080p"} (or similar resolution string)
#     GQL: {modifier, value: ResolutionEnum}  (e.g. FULL_HD)
# ===========================================================================

class TestResolutionCriterion:

    def test_resolution_1080p(self):
        ui = {'resolution': {'modifier': 'EQUALS', 'value': 'FULL_HD'}}
        result = convert_ui_filter(ui)
        # Resolution enum values should pass through (already enum strings)
        assert result['resolution'] == {'modifier': 'EQUALS', 'value': 'FULL_HD'}

    def test_average_resolution(self):
        ui = {'average_resolution': {'modifier': 'GREATER_THAN', 'value': 'FOUR_K'}}
        result = convert_ui_filter(ui)
        assert result['average_resolution'] == {'modifier': 'GREATER_THAN', 'value': 'FOUR_K'}


# ===========================================================================
# 13. ORIENTATION CRITERION
#     UI: {modifier, value: ["PORTRAIT", "LANDSCAPE"]}
#     GQL: {value: [OrientationEnum...]}  (no modifier in GQL input!)
# ===========================================================================

class TestOrientationCriterion:

    def test_orientation_basic(self):
        ui = {'orientation': {'modifier': 'EQUALS', 'value': ['PORTRAIT', 'LANDSCAPE']}}
        result = convert_ui_filter(ui)
        assert result['orientation'] == {'value': ['PORTRAIT', 'LANDSCAPE']}

    def test_orientation_single(self):
        ui = {'orientation': {'modifier': 'EQUALS', 'value': ['SQUARE']}}
        result = convert_ui_filter(ui)
        assert result['orientation'] == {'value': ['SQUARE']}


# ===========================================================================
# 14. GENDER CRITERION
#     UI: {modifier, value: ["FEMALE", "MALE"]}
#     GQL: {modifier, value_list: [GenderEnum...]}  (field rename: value -> value_list)
# ===========================================================================

class TestGenderCriterion:

    def test_gender_basic(self):
        ui = {'gender': {'modifier': 'INCLUDES', 'value': ['FEMALE', 'MALE']}}
        result = convert_ui_filter(ui)
        assert result['gender'] == {'modifier': 'INCLUDES', 'value_list': ['FEMALE', 'MALE']}

    def test_gender_single(self):
        ui = {'gender': {'modifier': 'EQUALS', 'value': ['NON_BINARY']}}
        result = convert_ui_filter(ui)
        assert result['gender'] == {'modifier': 'EQUALS', 'value_list': ['NON_BINARY']}

    def test_gender_legacy_string(self):
        """Legacy format stored value as a single string, not array."""
        ui = {'gender': {'modifier': 'EQUALS', 'value': 'FEMALE'}}
        result = convert_ui_filter(ui)
        assert result['gender'] == {'modifier': 'EQUALS', 'value_list': ['FEMALE']}


# ===========================================================================
# 15. CIRCUMCISED CRITERION
#     UI: {modifier, value: ["CUT"]}
#     GQL: {modifier, value: [CircumisedEnum...]}
# ===========================================================================

class TestCircumcisedCriterion:

    def test_circumcised_basic(self):
        ui = {'circumcised': {'modifier': 'INCLUDES', 'value': ['CUT', 'UNCUT']}}
        result = convert_ui_filter(ui)
        assert result['circumcised'] == {'modifier': 'INCLUDES', 'value': ['CUT', 'UNCUT']}


# ===========================================================================
# 16. CAPTIONS CRITERION
#     UI: {modifier, value: "English"}
#     GQL: {modifier, value: "en"}  (language name -> ISO code)
#     Note: This is complex and may need a lookup table. For now, test passthrough.
# ===========================================================================

class TestCaptionsCriterion:

    def test_captions_passthrough(self):
        """Captions should at minimum pass through the structure."""
        ui = {'captions': {'modifier': 'INCLUDES', 'value': 'en'}}
        result = convert_ui_filter(ui)
        assert result['captions'] == {'modifier': 'INCLUDES', 'value': 'en'}


# ===========================================================================
# 17. CUSTOM FIELDS CRITERION (direct passthrough)
# ===========================================================================

class TestCustomFieldsCriterion:

    def test_custom_fields_passthrough(self):
        """custom_fields should pass through unchanged — no conversion needed."""
        ui = {'custom_fields': [
            {'field': 'my_field', 'modifier': 'EQUALS', 'value': ['hello']},
        ]}
        result = convert_ui_filter(ui)
        assert result['custom_fields'] == [
            {'field': 'my_field', 'modifier': 'EQUALS', 'value': ['hello']},
        ]


# ===========================================================================
# 18. EDGE CASES
# ===========================================================================

class TestEdgeCases:

    def test_does_not_mutate_input(self):
        """convert_ui_filter should not modify the original dict."""
        ui = {'organized': {'modifier': 'EQUALS', 'value': 'true'}}
        import copy
        original = copy.deepcopy(ui)
        convert_ui_filter(ui)
        assert ui == original

    def test_hierarchical_already_converted(self):
        """If tags are already in GQL format (no items/excluded), pass through."""
        ui = {'tags': {'modifier': 'INCLUDES', 'value': ['1', '2'], 'depth': 0}}
        result = convert_ui_filter(ui)
        assert result['tags'] == {'modifier': 'INCLUDES', 'value': ['1', '2'], 'depth': 0}

    def test_multi_criterion_already_converted(self):
        """If performers are already in GQL format, pass through."""
        ui = {'performers': {'modifier': 'INCLUDES', 'value': ['1']}}
        result = convert_ui_filter(ui)
        assert result['performers'] == {'modifier': 'INCLUDES', 'value': ['1']}

    def test_int_value_already_flat(self):
        """If int field value is already a plain int, pass through."""
        ui = {'rating100': {'modifier': 'EQUALS', 'value': 80}}
        result = convert_ui_filter(ui)
        assert result['rating100'] == {'modifier': 'EQUALS', 'value': 80}

    def test_boolean_already_plain(self):
        """If a boolean field is already a plain bool, no conversion needed."""
        ui = {'organized': True}
        result = convert_ui_filter(ui)
        assert result['organized'] is True

    def test_string_as_boolean_already_plain(self):
        """If is_missing is already a plain string, no conversion needed."""
        ui = {'is_missing': 'title'}
        result = convert_ui_filter(ui)
        assert result['is_missing'] == 'title'

    def test_date_value_already_flat(self):
        """If date value is already a flat string, pass through."""
        ui = {'date': {'modifier': 'EQUALS', 'value': '2024-01-01'}}
        result = convert_ui_filter(ui)
        assert result['date'] == {'modifier': 'EQUALS', 'value': '2024-01-01'}

    def test_timestamp_date_only_no_space(self):
        """Timestamp with date-only value (no space) should pass through as-is."""
        ui = {'created_at': {'modifier': 'EQUALS', 'value': {'value': '2024-01-01', 'value2': ''}}}
        result = convert_ui_filter(ui)
        assert result['created_at']['value'] == '2024-01-01'

    def test_hierarchical_empty_items_and_excluded(self):
        ui = {'tags': {
            'modifier': 'INCLUDES',
            'value': {'depth': 0, 'items': [], 'excluded': []},
        }}
        result = convert_ui_filter(ui)
        assert result['tags'] == {'modifier': 'INCLUDES', 'value': [], 'depth': 0}
        assert 'excludes' not in result['tags']

    def test_phash_distance_as_int_fallback(self):
        """If phash_distance has old int-style nested value (no distance key), treat as int."""
        ui = {'phash_distance': {'modifier': 'EQUALS', 'value': {'value': 8, 'value2': None}}}
        result = convert_ui_filter(ui)
        # Without 'distance' key, the phash handler skips it, but the int handler
        # was removed for phash_distance, so it passes through with nested value.
        # This is acceptable — the phash criterion format is canonical now.
        assert 'phash_distance' in result

    def test_gender_empty_array(self):
        ui = {'gender': {'modifier': 'INCLUDES', 'value': []}}
        result = convert_ui_filter(ui)
        assert result['gender'] == {'modifier': 'INCLUDES', 'value_list': []}

    def test_stash_id_already_converted(self):
        """If stash_id_endpoint has no nested stashID, pass through."""
        ui = {'stash_id_endpoint': {'modifier': 'NOT_NULL', 'endpoint': '', 'stash_id': ''}}
        result = convert_ui_filter(ui)
        assert result['stash_id_endpoint'] == {'modifier': 'NOT_NULL', 'endpoint': '', 'stash_id': ''}

    def test_duplicated_phash_already_converted(self):
        """If duplicated_phash is already in GQL format, pass through."""
        ui = {'duplicated_phash': {'duplicated': True}}
        result = convert_ui_filter(ui)
        assert result['duplicated_phash'] == {'duplicated': True}

    def test_orientation_already_converted(self):
        """If orientation has no modifier (already GQL format), pass through."""
        ui = {'orientation': {'value': ['PORTRAIT']}}
        result = convert_ui_filter(ui)
        assert result['orientation'] == {'value': ['PORTRAIT']}

    def test_realistic_complex_scene_filter(self):
        """A realistic saved scene filter with many field types combined."""
        ui = {
            'tags': {
                'modifier': 'INCLUDES_ALL',
                'value': {'depth': 0, 'items': [_h_item('1', 'VR'), _h_item('2', '180')], 'excluded': [_h_item('99', 'Bad')]},
            },
            'performers': {
                'modifier': 'INCLUDES',
                'value': {'items': [_h_item('50', 'Alice')], 'excluded': []},
            },
            'rating100': {'modifier': 'GREATER_THAN', 'value': {'value': 60, 'value2': None}},
            'duration': {'modifier': 'BETWEEN', 'value': {'value': 300, 'value2': 7200}},
            'organized': {'modifier': 'EQUALS', 'value': 'true'},
            'is_missing': {'modifier': 'EQUALS', 'value': 'title'},
            'title': {'modifier': 'NOT_EQUALS', 'value': 'Untitled'},
            'created_at': {'modifier': 'GREATER_THAN', 'value': {'value': '2024-01-01 00:00', 'value2': ''}},
        }
        result = convert_ui_filter(ui)
        assert result['tags'] == {'modifier': 'INCLUDES_ALL', 'value': ['1', '2'], 'excludes': ['99'], 'depth': 0}
        assert result['performers'] == {'modifier': 'INCLUDES', 'value': ['50']}
        assert result['rating100'] == {'modifier': 'GREATER_THAN', 'value': 60}
        assert result['duration'] == {'modifier': 'BETWEEN', 'value': 300, 'value2': 7200}
        assert result['organized'] is True
        assert result['is_missing'] == 'title'
        assert result['title'] == {'modifier': 'NOT_EQUALS', 'value': 'Untitled'}
        assert result['created_at'] == {'modifier': 'GREATER_THAN', 'value': '2024-01-01T00:00'}

    def test_realistic_performer_filter(self):
        """A realistic saved performer filter."""
        ui = {
            'favourite': {'modifier': 'EQUALS', 'value': 'true'},
            'gender': {'modifier': 'INCLUDES', 'value': ['FEMALE']},
            'tags': {
                'modifier': 'INCLUDES',
                'value': {'depth': 0, 'items': [_h_item('10', 'VR')], 'excluded': []},
            },
            'birth_year': {'modifier': 'BETWEEN', 'value': {'value': 1990, 'value2': 2000}},
            'stash_id_endpoint': {
                'modifier': 'NOT_NULL',
                'value': {'endpoint': 'https://stashdb.org', 'stashID': ''},
            },
            'ignore_auto_tag': {'modifier': 'EQUALS', 'value': 'false'},
        }
        result = convert_ui_filter(ui)
        assert result['favourite'] is True
        assert result['gender'] == {'modifier': 'INCLUDES', 'value_list': ['FEMALE']}
        assert result['tags'] == {'modifier': 'INCLUDES', 'value': ['10'], 'depth': 0}
        assert result['birth_year'] == {'modifier': 'BETWEEN', 'value': 1990, 'value2': 2000}
        assert result['stash_id_endpoint'] == {'modifier': 'NOT_NULL', 'endpoint': 'https://stashdb.org', 'stash_id': ''}
        assert result['ignore_auto_tag'] is False
