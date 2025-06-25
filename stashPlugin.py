# Copyright 2023 Zyquo Onrel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Entry point for the Stash plugin.

import sys
import json

# from . import log

print(f'Read input from stdin, tty: {sys.stdin.isatty()}')
json_input = json.loads(sys.stdin.read())
print(f'Input:\n{json.dumps(json_input, indent=2)}')
name = json_input['args']['name']

# log.debug(f'Foo')
# log.debug(f'Bar: {name}')
# subprocess.Popen([some_path, path])