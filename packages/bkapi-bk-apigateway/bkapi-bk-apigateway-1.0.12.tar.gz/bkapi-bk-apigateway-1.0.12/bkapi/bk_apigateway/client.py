# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup, bind_property


class Group(OperationGroup):
    # bkapi resource add_related_apps
    # 添加网关关联应用
    add_related_apps = bind_property(
        Operation,
        name="add_related_apps",
        method="POST",
        path="/api/v1/apis/{api_name}/related-apps/",
    )

    # bkapi resource apply_permissions
    # 申请网关API访问权限
    apply_permissions = bind_property(
        Operation,
        name="apply_permissions",
        method="POST",
        path="/api/v1/apis/{api_name}/permissions/apply/",
    )

    # bkapi resource create_resource_version
    # 创建资源版本
    create_resource_version = bind_property(
        Operation,
        name="create_resource_version",
        method="POST",
        path="/api/v1/apis/{api_name}/resource_versions/",
    )

    # bkapi resource generate_sdk
    # 生成 SDK
    generate_sdk = bind_property(
        Operation,
        name="generate_sdk",
        method="POST",
        path="/api/v1/apis/{api_name}/sdk/",
    )

    # bkapi resource get_apigw_public_key
    # 获取网关公钥
    get_apigw_public_key = bind_property(
        Operation,
        name="get_apigw_public_key",
        method="GET",
        path="/api/v1/apis/{api_name}/public_key/",
    )

    # bkapi resource get_apis
    # 查询网关
    get_apis = bind_property(
        Operation,
        name="get_apis",
        method="GET",
        path="/api/v1/apis/",
    )

    # bkapi resource get_latest_resource_version
    # 获取网关最新版本
    get_latest_resource_version = bind_property(
        Operation,
        name="get_latest_resource_version",
        method="GET",
        path="/api/v1/apis/{api_name}/resource_versions/latest/",
    )

    # bkapi resource get_micro_gateway_app_permissions
    # 获取微网关应用权限
    get_micro_gateway_app_permissions = bind_property(
        Operation,
        name="get_micro_gateway_app_permissions",
        method="GET",
        path="/api/v1/edge-controller/micro-gateway/{instance_id}/permissions/",
    )

    # bkapi resource get_micro_gateway_info
    # 获取微网关信息
    get_micro_gateway_info = bind_property(
        Operation,
        name="get_micro_gateway_info",
        method="GET",
        path="/api/v1/edge-controller/micro-gateway/{instance_id}/gateway/",
    )

    # bkapi resource get_micro_gateway_newest_gateway_permissions
    # 获取微网关新添加的网关权限
    get_micro_gateway_newest_gateway_permissions = bind_property(
        Operation,
        name="get_micro_gateway_newest_gateway_permissions",
        method="GET",
        path="/api/v1/edge-controller/micro-gateway/{instance_id}/permissions/gateway/newest/",
    )

    # bkapi resource get_micro_gateway_newest_resource_permissions
    # 获取微网关新添加的网关权限
    get_micro_gateway_newest_resource_permissions = bind_property(
        Operation,
        name="get_micro_gateway_newest_resource_permissions",
        method="GET",
        path="/api/v1/edge-controller/micro-gateway/{instance_id}/permissions/resource/newest/",
    )

    # bkapi resource get_released_resource
    # 查询发布资源详情(包含接口参数)
    get_released_resource = bind_property(
        Operation,
        name="get_released_resource",
        method="GET",
        path="/api/v1/apis/{api_name}/released/stages/{stage_name}/resources/{resource_name}/",
    )

    # bkapi resource get_released_resources
    # 查询已发布资源列表
    get_released_resources = bind_property(
        Operation,
        name="get_released_resources",
        method="GET",
        path="/api/v1/apis/{api_name}/released/stages/{stage_name}/resources/",
    )

    # bkapi resource get_stages
    # 查询环境
    get_stages = bind_property(
        Operation,
        name="get_stages",
        method="GET",
        path="/api/v1/apis/{api_name}/stages/",
    )

    # bkapi resource get_stages_with_resource_version
    # 查询网关环境资源版本
    get_stages_with_resource_version = bind_property(
        Operation,
        name="get_stages_with_resource_version",
        method="GET",
        path="/api/v1/apis/{api_name}/stages/with-resource-version/",
    )

    # bkapi resource grant_permissions
    # 网关为应用主动授权
    grant_permissions = bind_property(
        Operation,
        name="grant_permissions",
        method="POST",
        path="/api/v1/apis/{api_name}/permissions/grant/",
    )

    # bkapi resource import_resource_docs_by_archive
    # 通过文档归档文件导入资源文档
    import_resource_docs_by_archive = bind_property(
        Operation,
        name="import_resource_docs_by_archive",
        method="POST",
        path="/api/v1/apis/{api_name}/resource-docs/import/by-archive/",
    )

    # bkapi resource import_resource_docs_by_swagger
    # 通过 Swagger 格式导入文档
    import_resource_docs_by_swagger = bind_property(
        Operation,
        name="import_resource_docs_by_swagger",
        method="POST",
        path="/api/v1/apis/{api_name}/resource-docs/import/by-swagger/",
    )

    # bkapi resource list_resource_versions
    # 查询资源版本
    list_resource_versions = bind_property(
        Operation,
        name="list_resource_versions",
        method="GET",
        path="/api/v1/apis/{api_name}/resource_versions/",
    )

    # bkapi resource mcp_proxy_application_message
    # mcp proxy message(应用态)接口
    mcp_proxy_application_message = bind_property(
        Operation,
        name="mcp_proxy_application_message",
        method="POST",
        path="/api/v2/mcp-servers/{mcp_server_name}/application/sse/message",
    )

    # bkapi resource mcp_proxy_application_sse
    # mcp proxy sse(应用态)接口
    mcp_proxy_application_sse = bind_property(
        Operation,
        name="mcp_proxy_application_sse",
        method="GET",
        path="/api/v2/mcp-servers/{mcp_server_name}/application/sse",
    )

    # bkapi resource mcp_proxy_message
    # mcp proxy message接口
    mcp_proxy_message = bind_property(
        Operation,
        name="mcp_proxy_message",
        method="POST",
        path="/api/v2/mcp-servers/{mcp_server_name}/sse/message",
    )

    # bkapi resource mcp_proxy_sse
    # mcp proxy sse接口
    mcp_proxy_sse = bind_property(
        Operation,
        name="mcp_proxy_sse",
        method="GET",
        path="/api/v2/mcp-servers/{mcp_server_name}/sse",
    )

    # bkapi resource release
    # 发布版本
    release = bind_property(
        Operation,
        name="release",
        method="POST",
        path="/api/v1/apis/{api_name}/resource_versions/release/",
    )

    # bkapi resource revoke_permissions
    # 回收应用访问网关 API 的权限
    revoke_permissions = bind_property(
        Operation,
        name="revoke_permissions",
        method="DELETE",
        path="/api/v1/apis/{api_name}/permissions/revoke/",
    )

    # bkapi resource sync_access_strategy
    # 同步策略
    sync_access_strategy = bind_property(
        Operation,
        name="sync_access_strategy",
        method="POST",
        path="/api/v1/apis/{api_name}/access_strategies/sync/",
    )

    # bkapi resource sync_api
    # 同步网关
    sync_api = bind_property(
        Operation,
        name="sync_api",
        method="POST",
        path="/api/v1/apis/{api_name}/sync/",
    )

    # bkapi resource sync_resources
    # 同步资源
    sync_resources = bind_property(
        Operation,
        name="sync_resources",
        method="POST",
        path="/api/v1/apis/{api_name}/resources/sync/",
    )

    # bkapi resource sync_stage
    # 同步环境
    sync_stage = bind_property(
        Operation,
        name="sync_stage",
        method="POST",
        path="/api/v1/apis/{api_name}/stages/sync/",
    )

    # bkapi resource update_gateway_status
    # 修改网关状态
    update_gateway_status = bind_property(
        Operation,
        name="update_gateway_status",
        method="POST",
        path="/api/v1/apis/{api_name}/status/",
    )

    # bkapi resource update_micro_gateway_status
    # 更新微网关实例状态
    update_micro_gateway_status = bind_property(
        Operation,
        name="update_micro_gateway_status",
        method="PUT",
        path="/api/v1/edge-controller/micro-gateway/{instance_id}/status/",
    )

    # bkapi resource v2_inner_apply_esb_system_component_permissions
    # 创建申请ESB组件权限的申请单据
    v2_inner_apply_esb_system_component_permissions = bind_property(
        Operation,
        name="v2_inner_apply_esb_system_component_permissions",
        method="POST",
        path="/api/v2/inner/esb/systems/{system_id}/permissions/apply/",
    )

    # bkapi resource v2_inner_apply_gateway_resource_permission
    # 网关资源权限申请
    v2_inner_apply_gateway_resource_permission = bind_property(
        Operation,
        name="v2_inner_apply_gateway_resource_permission",
        method="POST",
        path="/api/v2/inner/gateways/{gateway_name}/permissions/app-permissions/apply/",
    )

    # bkapi resource v2_inner_apply_mcp_server_permission
    # mcp_server 权限申请/批量申请
    v2_inner_apply_mcp_server_permission = bind_property(
        Operation,
        name="v2_inner_apply_mcp_server_permission",
        method="POST",
        path="/api/v2/inner/mcp-server/permissions/apply/",
    )

    # bkapi resource v2_inner_check_is_allowed_apply_by_gateway
    # 是否允许按网关申请资源权限
    v2_inner_check_is_allowed_apply_by_gateway = bind_property(
        Operation,
        name="v2_inner_check_is_allowed_apply_by_gateway",
        method="GET",
        path="/api/v2/inner/gateways/{gateway_name}/permissions/app-permissions/allow-apply-by-gateway/",
    )

    # bkapi resource v2_inner_get_app_esb_component_permission_apply_record
    # 查询应用权限申请记录详情
    v2_inner_get_app_esb_component_permission_apply_record = bind_property(
        Operation,
        name="v2_inner_get_app_esb_component_permission_apply_record",
        method="GET",
        path="/api/v2/inner/esb/systems/permissions/apply-records/{record_id}/",
    )

    # bkapi resource v2_inner_get_gateway
    # 获取网关
    v2_inner_get_gateway = bind_property(
        Operation,
        name="v2_inner_get_gateway",
        method="GET",
        path="/api/v2/inner/gateways/{gateway_name}/",
    )

    # bkapi resource v2_inner_list_app_esb_component_permission_apply_records
    # 查询应用权限申请记录列表
    v2_inner_list_app_esb_component_permission_apply_records = bind_property(
        Operation,
        name="v2_inner_list_app_esb_component_permission_apply_records",
        method="GET",
        path="/api/v2/inner/esb/systems/permissions/apply-records/",
    )

    # bkapi resource v2_inner_list_app_esb_component_permissions
    # 已申请权限列表
    v2_inner_list_app_esb_component_permissions = bind_property(
        Operation,
        name="v2_inner_list_app_esb_component_permissions",
        method="GET",
        path="/api/v2/inner/esb/systems/permissions/app-permissions/",
    )

    # bkapi resource v2_inner_list_app_resource_permissions
    # 已申请权限列表
    v2_inner_list_app_resource_permissions = bind_property(
        Operation,
        name="v2_inner_list_app_resource_permissions",
        method="GET",
        path="/api/v2/inner/gateways/permissions/app-permissions/",
    )

    # bkapi resource v2_inner_list_esb_system_permission_components
    # 查询系统权限组件
    v2_inner_list_esb_system_permission_components = bind_property(
        Operation,
        name="v2_inner_list_esb_system_permission_components",
        method="GET",
        path="/api/v2/inner/esb/systems/{system_id}/permissions/components/",
    )

    # bkapi resource v2_inner_list_esb_systems
    # 查询组件系统列表
    v2_inner_list_esb_systems = bind_property(
        Operation,
        name="v2_inner_list_esb_systems",
        method="GET",
        path="/api/v2/inner/esb/systems/",
    )

    # bkapi resource v2_inner_list_gateway_permission_resources
    # 获取网关资源
    v2_inner_list_gateway_permission_resources = bind_property(
        Operation,
        name="v2_inner_list_gateway_permission_resources",
        method="GET",
        path="/api/v2/inner/gateways/{gateway_name}/permissions/resources/",
    )

    # bkapi resource v2_inner_list_gateways
    # 获取网关列表
    v2_inner_list_gateways = bind_property(
        Operation,
        name="v2_inner_list_gateways",
        method="GET",
        path="/api/v2/inner/gateways/",
    )

    # bkapi resource v2_inner_list_mcp_server_app_permissions
    # mcp_server 已申请权限列表
    v2_inner_list_mcp_server_app_permissions = bind_property(
        Operation,
        name="v2_inner_list_mcp_server_app_permissions",
        method="GET",
        path="/api/v2/inner/mcp-server/permissions/app-permissions/",
    )

    # bkapi resource v2_inner_list_mcp_server_permission_apply_records
    # mcp_server 申请记录列表
    v2_inner_list_mcp_server_permission_apply_records = bind_property(
        Operation,
        name="v2_inner_list_mcp_server_permission_apply_records",
        method="GET",
        path="/api/v2/inner/mcp-server/permissions/apply-records/",
    )

    # bkapi resource v2_inner_list_mcp_server_permissions
    # mcp_server 申请权限列表
    v2_inner_list_mcp_server_permissions = bind_property(
        Operation,
        name="v2_inner_list_mcp_server_permissions",
        method="GET",
        path="/api/v2/inner/mcp-server/permissions/",
    )

    # bkapi resource v2_inner_list_resource_permission_apply_records
    # 资源权限申请记录
    v2_inner_list_resource_permission_apply_records = bind_property(
        Operation,
        name="v2_inner_list_resource_permission_apply_records",
        method="GET",
        path="/api/v2/inner/gateways/permissions/apply-records/",
    )

    # bkapi resource v2_inner_renew_esb_component_permissions
    # ESB 组件权限续期
    v2_inner_renew_esb_component_permissions = bind_property(
        Operation,
        name="v2_inner_renew_esb_component_permissions",
        method="POST",
        path="/api/v2/inner/esb/systems/permissions/renew/",
    )

    # bkapi resource v2_inner_renew_resource_permission
    # 权限续期
    v2_inner_renew_resource_permission = bind_property(
        Operation,
        name="v2_inner_renew_resource_permission",
        method="POST",
        path="/api/v2/inner/gateways/permissions/renew/",
    )

    # bkapi resource v2_inner_retrieve_mcp_server_permission_apply_record
    # mcp_server 申请记录详情
    v2_inner_retrieve_mcp_server_permission_apply_record = bind_property(
        Operation,
        name="v2_inner_retrieve_mcp_server_permission_apply_record",
        method="GET",
        path="/api/v2/inner/mcp-server/permissions/apply-records/{record_id}/",
    )

    # bkapi resource v2_inner_retrieve_resource_permission_apply_record
    # 资源权限申请记录详情
    v2_inner_retrieve_resource_permission_apply_record = bind_property(
        Operation,
        name="v2_inner_retrieve_resource_permission_apply_record",
        method="GET",
        path="/api/v2/inner/gateways/permissions/apply-records/{record_id}/",
    )

    # bkapi resource v2_open_apply_gateway_permission
    # 申请网关权限
    v2_open_apply_gateway_permission = bind_property(
        Operation,
        name="v2_open_apply_gateway_permission",
        method="POST",
        path="/api/v2/open/gateways/{gateway_name}/permissions/apply/",
    )

    # bkapi resource v2_open_get_gateway
    # 获取网关
    v2_open_get_gateway = bind_property(
        Operation,
        name="v2_open_get_gateway",
        method="GET",
        path="/api/v2/open/gateways/{gateway_name}/",
    )

    # bkapi resource v2_open_get_gateway_public_key
    # 获取网关公钥(废弃)
    v2_open_get_gateway_public_key = bind_property(
        Operation,
        name="v2_open_get_gateway_public_key",
        method="GET",
        path="/api/v2/open/gateway/{gateway_name}/public_key/",
    )

    # bkapi resource v2_open_get_gateway_public_key_new
    # 获取网关公钥
    v2_open_get_gateway_public_key_new = bind_property(
        Operation,
        name="v2_open_get_gateway_public_key_new",
        method="GET",
        path="/api/v2/open/gateways/{gateway_name}/public_key/",
    )

    # bkapi resource v2_open_list_gateways
    # 获取网关列表
    v2_open_list_gateways = bind_property(
        Operation,
        name="v2_open_list_gateways",
        method="GET",
        path="/api/v2/open/gateways/",
    )

    # bkapi resource v2_open_list_mcp_server
    # 获取公开的 mcp_server 列表
    v2_open_list_mcp_server = bind_property(
        Operation,
        name="v2_open_list_mcp_server",
        method="GET",
        path="/api/v2/open/mcp-servers/",
    )

    # bkapi resource v2_open_list_mcp_server_app_permissions
    # 获取 app_code 的权限列表
    v2_open_list_mcp_server_app_permissions = bind_property(
        Operation,
        name="v2_open_list_mcp_server_app_permissions",
        method="GET",
        path="/api/v2/open/mcp-servers/permissions/",
    )

    # bkapi resource v2_open_list_mcp_server_app_permissions_apply_records
    # 获取指定应用的 mcp_server 权限申请记录列表
    v2_open_list_mcp_server_app_permissions_apply_records = bind_property(
        Operation,
        name="v2_open_list_mcp_server_app_permissions_apply_records",
        method="GET",
        path="/api/v2/open/mcp-servers/permissions/apply-records/",
    )

    # bkapi resource v2_open_list_mcp_server_permissions
    # 获取 mcp_server 的权限列表
    v2_open_list_mcp_server_permissions = bind_property(
        Operation,
        name="v2_open_list_mcp_server_permissions",
        method="GET",
        path="/api/v2/open/mcp-servers/{mcp_server_id}/permissions/",
    )

    # bkapi resource v2_open_list_user_mcp_server
    # 获取 mcp_server 列表
    v2_open_list_user_mcp_server = bind_property(
        Operation,
        name="v2_open_list_user_mcp_server",
        method="GET",
        path="/api/v2/open/user/mcp-servers/",
    )

    # bkapi resource v2_open_mcp_server_app_permissions_apply
    # 指定应用发起 mcp_server 权限申请
    v2_open_mcp_server_app_permissions_apply = bind_property(
        Operation,
        name="v2_open_mcp_server_app_permissions_apply",
        method="POST",
        path="/api/v2/open/mcp-servers/permissions/apply/",
    )

    # bkapi resource v2_sync_add_related_apps
    # 添加网关的关联应用
    v2_sync_add_related_apps = bind_property(
        Operation,
        name="v2_sync_add_related_apps",
        method="POST",
        path="/api/v2/sync/gateways/{gateway_name}/related-apps/",
    )

    # bkapi resource v2_sync_create_resource_version
    # 网关资源版本创建
    v2_sync_create_resource_version = bind_property(
        Operation,
        name="v2_sync_create_resource_version",
        method="POST",
        path="/api/v2/sync/gateways/{gateway_name}/resource_versions/",
    )

    # bkapi resource v2_sync_gateway
    # 同步网关
    v2_sync_gateway = bind_property(
        Operation,
        name="v2_sync_gateway",
        method="POST",
        path="/api/v2/sync/gateways/{gateway_name}/",
    )

    # bkapi resource v2_sync_generate_sdk
    # 生成网关sdk
    v2_sync_generate_sdk = bind_property(
        Operation,
        name="v2_sync_generate_sdk",
        method="POST",
        path="/api/v2/sync/gateways/{gateway_name}/sdks/",
    )

    # bkapi resource v2_sync_get_gateway_public_key_new
    # 获取网关公钥
    v2_sync_get_gateway_public_key_new = bind_property(
        Operation,
        name="v2_sync_get_gateway_public_key_new",
        method="GET",
        path="/api/v2/sync/gateways/{gateway_name}/public_key/",
    )

    # bkapi resource v2_sync_get_latest_resource_version
    # 获取网关资源版本最新版本
    v2_sync_get_latest_resource_version = bind_property(
        Operation,
        name="v2_sync_get_latest_resource_version",
        method="GET",
        path="/api/v2/sync/gateways/{gateway_name}/resource_versions/latest",
    )

    # bkapi resource v2_sync_grant_permission
    # 网关权限授权
    v2_sync_grant_permission = bind_property(
        Operation,
        name="v2_sync_grant_permission",
        method="POST",
        path="/api/v2/sync/gateways/{gateway_name}/permissions/grant/",
    )

    # bkapi resource v2_sync_list_permissions
    # 获取网关权限列表
    v2_sync_list_permissions = bind_property(
        Operation,
        name="v2_sync_list_permissions",
        method="GET",
        path="/api/v2/sync/gateways/{gateway_name}/permissions/",
    )

    # bkapi resource v2_sync_list_resource_versions
    # 查询网关资源版本列表
    v2_sync_list_resource_versions = bind_property(
        Operation,
        name="v2_sync_list_resource_versions",
        method="GET",
        path="/api/v2/sync/gateways/{gateway_name}/resource_versions/",
    )

    # bkapi resource v2_sync_release
    # 网关资源版本发布
    v2_sync_release = bind_property(
        Operation,
        name="v2_sync_release",
        method="POST",
        path="/api/v2/sync/gateways/{gateway_name}/resource_versions/release/",
    )

    # bkapi resource v2_sync_resource_doc
    # 同步网关资源文档
    v2_sync_resource_doc = bind_property(
        Operation,
        name="v2_sync_resource_doc",
        method="POST",
        path="/api/v2/sync/gateways/{gateway_name}/resource-docs/",
    )

    # bkapi resource v2_sync_resources
    # 同步网关资源
    v2_sync_resources = bind_property(
        Operation,
        name="v2_sync_resources",
        method="POST",
        path="/api/v2/sync/gateways/{gateway_name}/resources/",
    )

    # bkapi resource v2_sync_stage_mcp_servers
    # 同步网关 stage mcp_servers
    v2_sync_stage_mcp_servers = bind_property(
        Operation,
        name="v2_sync_stage_mcp_servers",
        method="POST",
        path="/api/v2/sync/gateways/{gateway_name}/stages/{stage_name}/mcp-servers/",
    )

    # bkapi resource v2_sync_stages
    # 添加网关的关联应用
    v2_sync_stages = bind_property(
        Operation,
        name="v2_sync_stages",
        method="POST",
        path="/api/v2/sync/gateways/{gateway_name}/stages/",
    )


class Client(APIGatewayClient):
    """Bkapi bk_apigateway client"""
    _api_name = "bk-apigateway"

    api = bind_property(Group, name="api")
