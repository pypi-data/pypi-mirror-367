class ModelUrlConstant:
    T0KEN_HEADER_NAME = "X-Access-Token"
    TOKEN_LOGIN_TYPE_HEADER_NAME = "Login-Type"
    TOKEN_URL = "/jeecg-system/sys/sysApplication/getAppToken"
    UPLOAD = "/jeecg-system/sys/common/upload"
    SERVICE_GET_NC_SCHEMA_URL = "/szrs-model/model/slbModelServiceArgo/schSvcNcInfo"
    SERVICE_WRITE_SERVICE_NC_URL = (
        "/szrs-model/model/slbModelServiceArgo/writeServiceNcFile"
    )
    SERVICE_EXEC_SCHEME_SERVICE_URL = "/szrs-model/model/slbModelServiceArgo/schSvc"
    SERVICE_EXEC_SINGLE_SERVICE_STD_URL = (
        "/szrs-model/model/slbModelServiceVcJob/stdSvc"
    )
    SERVICE_EXEC_SINGLE_SERVICE_NSTD_URL = (
        "/szrs-model/model/slbModelServiceVcJob/stdNonSvc"
    )
    CORE_NC_TO_JSON_URL = "/szrs-model/model/slbModelCores/ncToJson"
    POSTPROCESS_GET_ALL_ACHIEVEMENTS_URL = (
        "/szrs-postprocess/baseAchievements/getAllAchievementBySchemeId"
    )
    POSTPROCESS_GET_LATEST_ACHIEVEMENTS_URL = (
        "/szrs-postprocess/baseAchievements/getAchievementBySchemeId"
    )
    POSTPROCESS_GET_ACHIEVEMENTS_FULL_URL = (
        "/szrs-postprocess/baseAchievements/getAchievementList"
    )
    POSTPROCESS_GET_ACHIEVEMENTS_BASE_GEO_URL = (
        "/szrs-postprocess/baseAchievements/getAchievementsBaseGeo"
    )
    POSTPROCESS_GET_ACHIEVEMENTS_DETAIL_URL = (
        "/szrs-postprocess/baseAchievements/getAchievementsElementDetail"
    )
    POSTPROCESS_GET_ACHIEVEMENTS_TIMELINE_URL = (
        "/szrs-postprocess/baseAchievements/getAchievementsElementTimeLine"
    )
