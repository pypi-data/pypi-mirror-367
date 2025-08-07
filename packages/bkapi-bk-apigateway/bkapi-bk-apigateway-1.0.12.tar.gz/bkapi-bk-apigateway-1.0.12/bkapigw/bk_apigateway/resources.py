# -*- coding: utf-8 -*-
from .base import RequestAPI


class CollectionsAPI(object):
    def __init__(self, client):
        from . import conf

        self.client = client
        self.host = conf.HOST.format(api_name="bk-apigateway")

        self.sync_api = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/sync/")

        self.sync_stage = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/stages/sync/")

        self.sync_resources = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/resources/sync/")

        self.create_resource_version = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/resource_versions/")

        self.sync_access_strategy = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/access_strategies/sync/")

        self.apply_permissions = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/permissions/apply/")

        self.get_apigw_public_key = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v1/apis/{api_name}/public_key/")

        self.get_latest_resource_version = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v1/apis/{api_name}/resource_versions/latest/")

        self.release = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/resource_versions/release/")

        self.grant_permissions = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/permissions/grant/")

        self.import_resource_docs_by_archive = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/resource-docs/import/by-archive/")

        self.import_resource_docs_by_swagger = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/resource-docs/import/by-swagger/")

        self.add_related_apps = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/related-apps/")

        self.revoke_permissions = RequestAPI(client=self.client, method="DELETE", host=self.host, path="/api/v1/apis/{api_name}/permissions/revoke/")

        self.update_micro_gateway_status = RequestAPI(client=self.client, method="PUT", host=self.host, path="/api/v1/edge-controller/micro-gateway/{instance_id}/status/")

        self.generate_sdk = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/sdk/")

        self.get_micro_gateway_app_permissions = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v1/edge-controller/micro-gateway/{instance_id}/permissions/")

        self.get_apis = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v1/apis/")

        self.get_stages = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v1/apis/{api_name}/stages/")

        self.get_released_resources = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v1/apis/{api_name}/released/stages/{stage_name}/resources/")

        self.get_micro_gateway_info = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v1/edge-controller/micro-gateway/{instance_id}/gateway/")

        self.get_micro_gateway_newest_gateway_permissions = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v1/edge-controller/micro-gateway/{instance_id}/permissions/gateway/newest/")

        self.get_micro_gateway_newest_resource_permissions = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v1/edge-controller/micro-gateway/{instance_id}/permissions/resource/newest/")

        self.get_stages_with_resource_version = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v1/apis/{api_name}/stages/with-resource-version/")

        self.update_gateway_status = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v1/apis/{api_name}/status/")

        self.list_resource_versions = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v1/apis/{api_name}/resource_versions/")

        self.get_released_resource = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v1/apis/{api_name}/released/stages/{stage_name}/resources/{resource_name}/")

        self.v2_sync_list_permissions = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/sync/gateways/{gateway_name}/permissions/")

        self.v2_inner_list_gateways = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/inner/gateways/")

        self.v2_inner_get_gateway = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/inner/gateways/{gateway_name}/")

        self.v2_open_get_gateway_public_key = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/open/gateway/{gateway_name}/public_key/")

        self.v2_open_list_gateways = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/open/gateways/")

        self.v2_open_get_gateway = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/open/gateways/{gateway_name}/")

        self.v2_open_get_gateway_public_key_new = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/open/gateways/{gateway_name}/public_key/")

        self.v2_sync_get_gateway_public_key_new = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/sync/gateways/{gateway_name}/public_key/")

        self.v2_sync_add_related_apps = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/sync/gateways/{gateway_name}/related-apps/")

        self.v2_inner_list_esb_systems = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/inner/esb/systems/")

        self.v2_inner_list_app_esb_component_permission_apply_records = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/inner/esb/systems/permissions/apply-records/")

        self.v2_inner_get_app_esb_component_permission_apply_record = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/inner/esb/systems/permissions/apply-records/{record_id}/")

        self.v2_inner_renew_esb_component_permissions = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/inner/esb/systems/permissions/renew/")

        self.v2_inner_list_esb_system_permission_components = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/inner/esb/systems/{system_id}/permissions/components/")

        self.v2_inner_list_app_resource_permissions = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/inner/gateways/permissions/app-permissions/")

        self.v2_inner_list_resource_permission_apply_records = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/inner/gateways/permissions/apply-records/")

        self.v2_inner_retrieve_resource_permission_apply_record = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/inner/gateways/permissions/apply-records/{record_id}/")

        self.v2_inner_renew_resource_permission = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/inner/gateways/permissions/renew/")

        self.v2_inner_check_is_allowed_apply_by_gateway = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/inner/gateways/{gateway_name}/permissions/app-permissions/allow-apply-by-gateway/")

        self.v2_inner_apply_gateway_resource_permission = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/inner/gateways/{gateway_name}/permissions/app-permissions/apply/")

        self.v2_inner_list_gateway_permission_resources = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/inner/gateways/{gateway_name}/permissions/resources/")

        self.v2_inner_list_mcp_server_permissions = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/inner/mcp-server/permissions/")

        self.v2_inner_list_mcp_server_app_permissions = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/inner/mcp-server/permissions/app-permissions/")

        self.v2_inner_list_mcp_server_permission_apply_records = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/inner/mcp-server/permissions/apply-records/")

        self.v2_inner_retrieve_mcp_server_permission_apply_record = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/inner/mcp-server/permissions/apply-records/{record_id}/")

        self.mcp_proxy_sse = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/mcp-servers/{mcp_server_name}/sse")

        self.mcp_proxy_message = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/mcp-servers/{mcp_server_name}/sse/message")

        self.v2_open_apply_gateway_permission = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/open/gateways/{gateway_name}/permissions/apply/")

        self.v2_sync_gateway = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/sync/gateways/{gateway_name}/")

        self.v2_sync_grant_permission = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/sync/gateways/{gateway_name}/permissions/grant/")

        self.v2_sync_resource_doc = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/sync/gateways/{gateway_name}/resource-docs/")

        self.v2_sync_list_resource_versions = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/sync/gateways/{gateway_name}/resource_versions/")

        self.v2_sync_create_resource_version = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/sync/gateways/{gateway_name}/resource_versions/")

        self.v2_sync_get_latest_resource_version = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/sync/gateways/{gateway_name}/resource_versions/latest")

        self.v2_sync_release = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/sync/gateways/{gateway_name}/resource_versions/release/")

        self.v2_sync_resources = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/sync/gateways/{gateway_name}/resources/")

        self.v2_sync_generate_sdk = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/sync/gateways/{gateway_name}/sdks/")

        self.v2_sync_stages = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/sync/gateways/{gateway_name}/stages/")

        self.v2_inner_list_app_esb_component_permissions = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/inner/esb/systems/permissions/app-permissions/")

        self.v2_inner_apply_esb_system_component_permissions = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/inner/esb/systems/{system_id}/permissions/apply/")

        self.v2_inner_apply_mcp_server_permission = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/inner/mcp-server/permissions/apply/")

        self.mcp_proxy_application_sse = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/mcp-servers/{mcp_server_name}/application/sse")

        self.mcp_proxy_application_message = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/mcp-servers/{mcp_server_name}/application/sse/message")

        self.v2_open_list_mcp_server = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/open/mcp-servers/")

        self.v2_open_list_mcp_server_app_permissions = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/open/mcp-servers/permissions/")

        self.v2_open_list_mcp_server_app_permissions_apply_records = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/open/mcp-servers/permissions/apply-records/")

        self.v2_open_mcp_server_app_permissions_apply = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/open/mcp-servers/permissions/apply/")

        self.v2_open_list_mcp_server_permissions = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/open/mcp-servers/{mcp_server_id}/permissions/")

        self.v2_open_list_user_mcp_server = RequestAPI(client=self.client, method="GET", host=self.host, path="/api/v2/open/user/mcp-servers/")

        self.v2_sync_stage_mcp_servers = RequestAPI(client=self.client, method="POST", host=self.host, path="/api/v2/sync/gateways/{gateway_name}/stages/{stage_name}/mcp-servers/")
