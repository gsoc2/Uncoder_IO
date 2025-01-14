"""
Uncoder IO Community Edition License
-----------------------------------------------------------------
Copyright (c) 2023 SOC Prime, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-----------------------------------------------------------------
"""
import json

from app.converter.platforms.splunk.renders.splunk import SplunkQueryRender, SplunkFieldValue
from app.converter.platforms.splunk.const import DEFAULT_SPLUNK_ALERT, splunk_alert_details
from app.converter.core.mapping import SourceMapping
from app.converter.core.models.platform_details import PlatformDetails
from app.converter.core.models.parser_output import MetaInfoContainer
from app.converter.tools.utils import get_rule_description_str


_AUTOGENERATED_TITLE = "Autogenerated Splunk Alert"


class SplunkAlertFieldValue(SplunkFieldValue):
    details: PlatformDetails = splunk_alert_details


class SplunkAlertRender(SplunkQueryRender):
    details: PlatformDetails = splunk_alert_details
    or_token = "OR"
    field_value_map = SplunkAlertFieldValue(or_token=or_token)

    def __create_mitre_threat(self, meta_info: MetaInfoContainer) -> dict:
        techniques = {'mitre_attack': []}

        for technique in meta_info.mitre_attack.get('techniques'):
            techniques['mitre_attack'].append(technique['technique_id'])

        return techniques

    def finalize_query(self, prefix: str, query: str, functions: str, meta_info: MetaInfoContainer,
                       source_mapping: SourceMapping = None, not_supported_functions: list = None):
        query = super().finalize_query(prefix=prefix, query=query, functions=functions, meta_info=meta_info)
        severity_map = {"critical": "4", "high": "3", "medium": "2", "low": "1"}
        rule = DEFAULT_SPLUNK_ALERT.replace("<query_place_holder>", query)
        rule = rule.replace("<title_place_holder>", meta_info.title or _AUTOGENERATED_TITLE)
        rule = rule.replace("<severity_place_holder>", severity_map.get(meta_info.severity, "1"))
        rule_description = get_rule_description_str(
            description=meta_info.description or 'Autogenerated Splunk Alert.',
            license=meta_info.license
        )
        rule = rule.replace("<description_place_holder>", rule_description)
        mitre_techniques = self.__create_mitre_threat(meta_info=meta_info)
        if mitre_techniques:
            mitre_str = f"action.correlationsearch.annotations = {mitre_techniques})"
            rule = rule.replace("<annotations_place_holder>", mitre_str)

        if not_supported_functions:
            rendered_not_supported = self.render_not_supported_functions(not_supported_functions)
            return rule + rendered_not_supported
        return rule
