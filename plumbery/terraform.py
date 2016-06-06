# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess
import graphviz

from plumbery.logging import plogging


class Terraform(object):
    def __init__(self, working_directory):
        self.working_directory = working_directory
        self.tf_path = os.getenv('TERRAFORM_PATH')
        if self.tf_path is None or not os.path.exists(self.tf_path):
            raise RuntimeError("Could not locate terraform binary. "
                               "Please check TERRAFORM_PATH ENV var.")

    def build(self, settings):
        tf_path = settings.get('tf_path', None)
        if tf_path is None:
            # default back to the directory of the fittings file.
            tf_path = self.working_directory

        parameters = settings.get('parameters', {})
        with open(os.path.join(tf_path, '.tfvars'), 'w') as tf_vars:
            for (key, value) in parameters.items():
                tf_vars.write('%s = "%s"' % (key, value))

        self._run_tf('apply', tf_path,
                     var_file=os.path.join(tf_path, '.tfvars'),
                     input=False)

    def graph(self, state_directory):
        graph_data = self._run_tf('graph', state_directory)
        graph = graphviz.Digraph
        graph_file_path = os.path.join(state_directory, 'multicloud.dot')
        with open(graph_file_path, 'w') as dot:
            dot.write(graph_data)
        graph.render(graph_file_path)

    def _run_tf(self, command, state_directory, **kwargs):
        params = [self.tf_path, command]
        for (key, value) in kwargs.items():
            params.append("-%s=%s" % (key.replace('_', '-'), value))
        params.append(state_directory)
        plogging.debug(params)
        out = subprocess.check_output(params)
        return out