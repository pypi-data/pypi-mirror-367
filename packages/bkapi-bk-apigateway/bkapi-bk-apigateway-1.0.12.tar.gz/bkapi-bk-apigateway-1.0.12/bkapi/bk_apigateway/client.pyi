# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup


class Group(OperationGroup):

    @property
    def add_related_apps(self) -> Operation:
        """
        bkapi resource add_related_apps
        添加网关关联应用
        """

    @property
    def apply_permissions(self) -> Operation:
        """
        bkapi resource apply_permissions
        申请网关API访问权限
        """

    @property
    def create_resource_version(self) -> Operation:
        """
        bkapi resource create_resource_version
        创建资源版本
        """

    @property
    def generate_sdk(self) -> Operation:
        """
        bkapi resource generate_sdk
        生成 SDK
        """

    @property
    def get_apigw_public_key(self) -> Operation:
        """
        bkapi resource get_apigw_public_key
        获取网关公钥
        """

    @property
    def get_apis(self) -> Operation:
        """
        bkapi resource get_apis
        查询网关
        """

    @property
    def get_latest_resource_version(self) -> Operation:
        """
        bkapi resource get_latest_resource_version
        获取网关最新版本
        """

    @property
    def get_micro_gateway_app_permissions(self) -> Operation:
        """
        bkapi resource get_micro_gateway_app_permissions
        获取微网关应用权限
        """

    @property
    def get_micro_gateway_info(self) -> Operation:
        """
        bkapi resource get_micro_gateway_info
        获取微网关信息
        """

    @property
    def get_micro_gateway_newest_gateway_permissions(self) -> Operation:
        """
        bkapi resource get_micro_gateway_newest_gateway_permissions
        获取微网关新添加的网关权限
        """

    @property
    def get_micro_gateway_newest_resource_permissions(self) -> Operation:
        """
        bkapi resource get_micro_gateway_newest_resource_permissions
        获取微网关新添加的网关权限
        """

    @property
    def get_released_resource(self) -> Operation:
        """
        bkapi resource get_released_resource
        查询发布资源详情(包含接口参数)
        """

    @property
    def get_released_resources(self) -> Operation:
        """
        bkapi resource get_released_resources
        查询已发布资源列表
        """

    @property
    def get_stages(self) -> Operation:
        """
        bkapi resource get_stages
        查询环境
        """

    @property
    def get_stages_with_resource_version(self) -> Operation:
        """
        bkapi resource get_stages_with_resource_version
        查询网关环境资源版本
        """

    @property
    def grant_permissions(self) -> Operation:
        """
        bkapi resource grant_permissions
        网关为应用主动授权
        """

    @property
    def import_resource_docs_by_archive(self) -> Operation:
        """
        bkapi resource import_resource_docs_by_archive
        通过文档归档文件导入资源文档
        """

    @property
    def import_resource_docs_by_swagger(self) -> Operation:
        """
        bkapi resource import_resource_docs_by_swagger
        通过 Swagger 格式导入文档
        """

    @property
    def list_resource_versions(self) -> Operation:
        """
        bkapi resource list_resource_versions
        查询资源版本
        """

    @property
    def mcp_proxy_application_message(self) -> Operation:
        """
        bkapi resource mcp_proxy_application_message
        mcp proxy message(应用态)接口
        """

    @property
    def mcp_proxy_application_sse(self) -> Operation:
        """
        bkapi resource mcp_proxy_application_sse
        mcp proxy sse(应用态)接口
        """

    @property
    def mcp_proxy_message(self) -> Operation:
        """
        bkapi resource mcp_proxy_message
        mcp proxy message接口
        """

    @property
    def mcp_proxy_sse(self) -> Operation:
        """
        bkapi resource mcp_proxy_sse
        mcp proxy sse接口
        """

    @property
    def release(self) -> Operation:
        """
        bkapi resource release
        发布版本
        """

    @property
    def revoke_permissions(self) -> Operation:
        """
        bkapi resource revoke_permissions
        回收应用访问网关 API 的权限
        """

    @property
    def sync_access_strategy(self) -> Operation:
        """
        bkapi resource sync_access_strategy
        同步策略
        """

    @property
    def sync_api(self) -> Operation:
        """
        bkapi resource sync_api
        同步网关
        """

    @property
    def sync_resources(self) -> Operation:
        """
        bkapi resource sync_resources
        同步资源
        """

    @property
    def sync_stage(self) -> Operation:
        """
        bkapi resource sync_stage
        同步环境
        """

    @property
    def update_gateway_status(self) -> Operation:
        """
        bkapi resource update_gateway_status
        修改网关状态
        """

    @property
    def update_micro_gateway_status(self) -> Operation:
        """
        bkapi resource update_micro_gateway_status
        更新微网关实例状态
        """

    @property
    def v2_inner_apply_esb_system_component_permissions(self) -> Operation:
        """
        bkapi resource v2_inner_apply_esb_system_component_permissions
        创建申请ESB组件权限的申请单据
        """

    @property
    def v2_inner_apply_gateway_resource_permission(self) -> Operation:
        """
        bkapi resource v2_inner_apply_gateway_resource_permission
        网关资源权限申请
        """

    @property
    def v2_inner_apply_mcp_server_permission(self) -> Operation:
        """
        bkapi resource v2_inner_apply_mcp_server_permission
        mcp_server 权限申请/批量申请
        """

    @property
    def v2_inner_check_is_allowed_apply_by_gateway(self) -> Operation:
        """
        bkapi resource v2_inner_check_is_allowed_apply_by_gateway
        是否允许按网关申请资源权限
        """

    @property
    def v2_inner_get_app_esb_component_permission_apply_record(self) -> Operation:
        """
        bkapi resource v2_inner_get_app_esb_component_permission_apply_record
        查询应用权限申请记录详情
        """

    @property
    def v2_inner_get_gateway(self) -> Operation:
        """
        bkapi resource v2_inner_get_gateway
        获取网关
        """

    @property
    def v2_inner_list_app_esb_component_permission_apply_records(self) -> Operation:
        """
        bkapi resource v2_inner_list_app_esb_component_permission_apply_records
        查询应用权限申请记录列表
        """

    @property
    def v2_inner_list_app_esb_component_permissions(self) -> Operation:
        """
        bkapi resource v2_inner_list_app_esb_component_permissions
        已申请权限列表
        """

    @property
    def v2_inner_list_app_resource_permissions(self) -> Operation:
        """
        bkapi resource v2_inner_list_app_resource_permissions
        已申请权限列表
        """

    @property
    def v2_inner_list_esb_system_permission_components(self) -> Operation:
        """
        bkapi resource v2_inner_list_esb_system_permission_components
        查询系统权限组件
        """

    @property
    def v2_inner_list_esb_systems(self) -> Operation:
        """
        bkapi resource v2_inner_list_esb_systems
        查询组件系统列表
        """

    @property
    def v2_inner_list_gateway_permission_resources(self) -> Operation:
        """
        bkapi resource v2_inner_list_gateway_permission_resources
        获取网关资源
        """

    @property
    def v2_inner_list_gateways(self) -> Operation:
        """
        bkapi resource v2_inner_list_gateways
        获取网关列表
        """

    @property
    def v2_inner_list_mcp_server_app_permissions(self) -> Operation:
        """
        bkapi resource v2_inner_list_mcp_server_app_permissions
        mcp_server 已申请权限列表
        """

    @property
    def v2_inner_list_mcp_server_permission_apply_records(self) -> Operation:
        """
        bkapi resource v2_inner_list_mcp_server_permission_apply_records
        mcp_server 申请记录列表
        """

    @property
    def v2_inner_list_mcp_server_permissions(self) -> Operation:
        """
        bkapi resource v2_inner_list_mcp_server_permissions
        mcp_server 申请权限列表
        """

    @property
    def v2_inner_list_resource_permission_apply_records(self) -> Operation:
        """
        bkapi resource v2_inner_list_resource_permission_apply_records
        资源权限申请记录
        """

    @property
    def v2_inner_renew_esb_component_permissions(self) -> Operation:
        """
        bkapi resource v2_inner_renew_esb_component_permissions
        ESB 组件权限续期
        """

    @property
    def v2_inner_renew_resource_permission(self) -> Operation:
        """
        bkapi resource v2_inner_renew_resource_permission
        权限续期
        """

    @property
    def v2_inner_retrieve_mcp_server_permission_apply_record(self) -> Operation:
        """
        bkapi resource v2_inner_retrieve_mcp_server_permission_apply_record
        mcp_server 申请记录详情
        """

    @property
    def v2_inner_retrieve_resource_permission_apply_record(self) -> Operation:
        """
        bkapi resource v2_inner_retrieve_resource_permission_apply_record
        资源权限申请记录详情
        """

    @property
    def v2_open_apply_gateway_permission(self) -> Operation:
        """
        bkapi resource v2_open_apply_gateway_permission
        申请网关权限
        """

    @property
    def v2_open_get_gateway(self) -> Operation:
        """
        bkapi resource v2_open_get_gateway
        获取网关
        """

    @property
    def v2_open_get_gateway_public_key(self) -> Operation:
        """
        bkapi resource v2_open_get_gateway_public_key
        获取网关公钥(废弃)
        """

    @property
    def v2_open_get_gateway_public_key_new(self) -> Operation:
        """
        bkapi resource v2_open_get_gateway_public_key_new
        获取网关公钥
        """

    @property
    def v2_open_list_gateways(self) -> Operation:
        """
        bkapi resource v2_open_list_gateways
        获取网关列表
        """

    @property
    def v2_open_list_mcp_server(self) -> Operation:
        """
        bkapi resource v2_open_list_mcp_server
        获取公开的 mcp_server 列表
        """

    @property
    def v2_open_list_mcp_server_app_permissions(self) -> Operation:
        """
        bkapi resource v2_open_list_mcp_server_app_permissions
        获取 app_code 的权限列表
        """

    @property
    def v2_open_list_mcp_server_app_permissions_apply_records(self) -> Operation:
        """
        bkapi resource v2_open_list_mcp_server_app_permissions_apply_records
        获取指定应用的 mcp_server 权限申请记录列表
        """

    @property
    def v2_open_list_mcp_server_permissions(self) -> Operation:
        """
        bkapi resource v2_open_list_mcp_server_permissions
        获取 mcp_server 的权限列表
        """

    @property
    def v2_open_list_user_mcp_server(self) -> Operation:
        """
        bkapi resource v2_open_list_user_mcp_server
        获取 mcp_server 列表
        """

    @property
    def v2_open_mcp_server_app_permissions_apply(self) -> Operation:
        """
        bkapi resource v2_open_mcp_server_app_permissions_apply
        指定应用发起 mcp_server 权限申请
        """

    @property
    def v2_sync_add_related_apps(self) -> Operation:
        """
        bkapi resource v2_sync_add_related_apps
        添加网关的关联应用
        """

    @property
    def v2_sync_create_resource_version(self) -> Operation:
        """
        bkapi resource v2_sync_create_resource_version
        网关资源版本创建
        """

    @property
    def v2_sync_gateway(self) -> Operation:
        """
        bkapi resource v2_sync_gateway
        同步网关
        """

    @property
    def v2_sync_generate_sdk(self) -> Operation:
        """
        bkapi resource v2_sync_generate_sdk
        生成网关sdk
        """

    @property
    def v2_sync_get_gateway_public_key_new(self) -> Operation:
        """
        bkapi resource v2_sync_get_gateway_public_key_new
        获取网关公钥
        """

    @property
    def v2_sync_get_latest_resource_version(self) -> Operation:
        """
        bkapi resource v2_sync_get_latest_resource_version
        获取网关资源版本最新版本
        """

    @property
    def v2_sync_grant_permission(self) -> Operation:
        """
        bkapi resource v2_sync_grant_permission
        网关权限授权
        """

    @property
    def v2_sync_list_permissions(self) -> Operation:
        """
        bkapi resource v2_sync_list_permissions
        获取网关权限列表
        """

    @property
    def v2_sync_list_resource_versions(self) -> Operation:
        """
        bkapi resource v2_sync_list_resource_versions
        查询网关资源版本列表
        """

    @property
    def v2_sync_release(self) -> Operation:
        """
        bkapi resource v2_sync_release
        网关资源版本发布
        """

    @property
    def v2_sync_resource_doc(self) -> Operation:
        """
        bkapi resource v2_sync_resource_doc
        同步网关资源文档
        """

    @property
    def v2_sync_resources(self) -> Operation:
        """
        bkapi resource v2_sync_resources
        同步网关资源
        """

    @property
    def v2_sync_stage_mcp_servers(self) -> Operation:
        """
        bkapi resource v2_sync_stage_mcp_servers
        同步网关 stage mcp_servers
        """

    @property
    def v2_sync_stages(self) -> Operation:
        """
        bkapi resource v2_sync_stages
        添加网关的关联应用
        """


class Client(APIGatewayClient):
    """Bkapi bk_apigateway client"""

    @property
    def api(self) -> OperationGroup:
        """api resources"""
