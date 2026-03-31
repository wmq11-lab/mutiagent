改进前：
{
  "repo_path": "/Users/admin/Desktop/potpie_bge",
  "changed_files": [
    ".env",
    ".env.template",
    "app/modules/intelligence/myprovider_client.py",
    "app/modules/intelligence/provider/llm_config.py",
    "app/modules/intelligence/provider/provider_service.py",
    "potpie-ui/.env"
  ],
  "impacted": [
    {
      "kind": "file",
      "id": ".env",
      "via": "changed_file",
      "depth": 0,
      "impact_type": [
        "config"
      ],
      "propagation_path": [
        ".env"
      ],
      "propagation_depth": 0,
      "propagation_type": "config",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "file",
      "id": ".env.template",
      "via": "changed_file",
      "depth": 0,
      "impact_type": [
        "config"
      ],
      "propagation_path": [
        ".env.template"
      ],
      "propagation_depth": 0,
      "propagation_type": "config",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "file",
      "id": "app/modules/intelligence/myprovider_client.py",
      "via": "changed_file",
      "depth": 0,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "app/modules/intelligence/myprovider_client.py"
      ],
      "propagation_depth": 0,
      "propagation_type": "call",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "file",
      "id": "app/modules/intelligence/provider/llm_config.py",
      "via": "changed_file",
      "depth": 0,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "app/modules/intelligence/provider/llm_config.py"
      ],
      "propagation_depth": 0,
      "propagation_type": "call",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "file",
      "id": "app/modules/intelligence/provider/provider_service.py",
      "via": "changed_file",
      "depth": 0,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "app/modules/intelligence/provider/provider_service.py"
      ],
      "propagation_depth": 0,
      "propagation_type": "call",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "file",
      "id": "potpie-ui/.env",
      "via": "changed_file",
      "depth": 0,
      "impact_type": [
        "config"
      ],
      "propagation_path": [
        "potpie-ui/.env"
      ],
      "propagation_depth": 0,
      "propagation_type": "config",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "symbol",
      "id": "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
      "via": "changed_entity",
      "depth": 0,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient"
      ],
      "propagation_depth": 0,
      "propagation_type": "exception",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:_stream_request",
      "via": "impact_seed:MyProviderClient",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/myprovider_client.py:dependency:_stream_request"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:getenv",
      "via": "impact_seed:MyProviderClient",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/myprovider_client.py:dependency:getenv"
      ],
      "propagation_depth": 0,
      "propagation_type": "config",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:iter_lines",
      "via": "impact_seed:MyProviderClient",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/myprovider_client.py:dependency:iter_lines"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:json",
      "via": "impact_seed:MyProviderClient",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/myprovider_client.py:dependency:json"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:loads",
      "via": "impact_seed:MyProviderClient",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/myprovider_client.py:dependency:loads"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:post",
      "via": "impact_seed:MyProviderClient",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/myprovider_client.py:dependency:post"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:raise_for_status",
      "via": "impact_seed:MyProviderClient",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/myprovider_client.py:dependency:raise_for_status"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:rstrip",
      "via": "impact_seed:MyProviderClient",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/myprovider_client.py:dependency:rstrip"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:split",
      "via": "impact_seed:MyProviderClient",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/myprovider_client.py:dependency:split"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:startswith",
      "via": "impact_seed:MyProviderClient",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/myprovider_client.py:dependency:startswith"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:strip",
      "via": "impact_seed:MyProviderClient",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/myprovider_client.py:dependency:strip"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:time",
      "via": "impact_seed:MyProviderClient",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/myprovider_client.py:dependency:time"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "symbol",
      "id": "app/modules/intelligence/myprovider_client.py:method:create_chat_completion",
      "via": "changed_entity",
      "depth": 0,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "propagation_depth": 0,
      "propagation_type": "exception",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:function:isinstance",
      "via": "impact_seed:create_chat_completion",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/myprovider_client.py:function:isinstance"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:variable:Exception",
      "via": "impact_seed:create_chat_completion",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/myprovider_client.py:variable:Exception"
      ],
      "propagation_depth": 0,
      "propagation_type": "exception",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:variable:ValueError",
      "via": "impact_seed:create_chat_completion",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/myprovider_client.py:variable:ValueError"
      ],
      "propagation_depth": 0,
      "propagation_type": "exception",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "symbol",
      "id": "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
      "via": "changed_entity",
      "depth": 0,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "propagation_depth": 0,
      "propagation_type": "call",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/llm_config.py:dependency:get",
      "via": "impact_seed:get_config_for_model",
      "depth": 1,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/llm_config.py:dependency:get"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/llm_config.py:function:parse_model_string",
      "via": "impact_seed:get_config_for_model",
      "depth": 1,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/llm_config.py:function:parse_model_string"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/llm_config.py:variable:Any",
      "via": "impact_seed:get_config_for_model",
      "depth": 1,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/llm_config.py:variable:Any"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/llm_config.py:variable:Dict",
      "via": "impact_seed:get_config_for_model",
      "depth": 1,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/llm_config.py:variable:Dict"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/llm_config.py:variable:MODEL_CONFIG_MAP",
      "via": "impact_seed:get_config_for_model",
      "depth": 1,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/llm_config.py:variable:MODEL_CONFIG_MAP"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/llm_config.py:variable:env_base_url",
      "via": "impact_seed:get_config_for_model",
      "depth": 1,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/llm_config.py:variable:env_base_url"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/llm_config.py:variable:fallback_auth_provider",
      "via": "impact_seed:get_config_for_model",
      "depth": 1,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/llm_config.py:variable:fallback_auth_provider"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/llm_config.py:variable:fallback_base_url",
      "via": "impact_seed:get_config_for_model",
      "depth": 1,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/llm_config.py:variable:fallback_base_url"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/llm_config.py:variable:model_string",
      "via": "impact_seed:get_config_for_model",
      "depth": 1,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/llm_config.py:variable:model_string"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/llm_config.py:variable:os",
      "via": "impact_seed:get_config_for_model",
      "depth": 1,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/llm_config.py:variable:os"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/llm_config.py:variable:parse_model_string",
      "via": "impact_seed:get_config_for_model",
      "depth": 1,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/llm_config.py:variable:parse_model_string"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/llm_config.py:variable:provider",
      "via": "impact_seed:get_config_for_model",
      "depth": 1,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/llm_config.py:variable:provider"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "symbol",
      "id": "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
      "via": "changed_entity",
      "depth": 0,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "propagation_depth": 0,
      "propagation_type": "exception",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:_build_config_for_model_identifier",
      "via": "impact_seed:ProviderService",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:_build_config_for_model_identifier"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:_build_llm_params",
      "via": "impact_seed:ProviderService",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:_build_llm_params"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:_format_anthropic_multimodal_message",
      "via": "impact_seed:ProviderService",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:_format_anthropic_multimodal_message"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:_format_gemini_multimodal_message",
      "via": "impact_seed:ProviderService",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:_format_gemini_multimodal_message"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:_format_multimodal_message",
      "via": "impact_seed:ProviderService",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:_format_multimodal_message"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:_format_multimodal_messages",
      "via": "impact_seed:ProviderService",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:_format_multimodal_messages"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:_format_openai_multimodal_message",
      "via": "impact_seed:ProviderService",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:_format_openai_multimodal_message"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:_get_api_key",
      "via": "impact_seed:ProviderService",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:_get_api_key"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:_validate_images_for_multimodal",
      "via": "impact_seed:ProviderService",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:_validate_images_for_multimodal"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:add",
      "via": "impact_seed:ProviderService",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:add"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:append",
      "via": "impact_seed:ProviderService",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:append"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:call_llm",
      "via": "impact_seed:ProviderService",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:call_llm"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "symbol",
      "id": "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
      "via": "changed_entity",
      "depth": 0,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "propagation_depth": 0,
      "propagation_type": "call",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:endswith",
      "via": "impact_seed:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:endswith"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:get",
      "via": "impact_seed:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:get"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:items",
      "via": "impact_seed:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:items"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:rstrip",
      "via": "impact_seed:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:rstrip"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:split",
      "via": "impact_seed:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:split"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:startswith",
      "via": "impact_seed:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:startswith"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:dependency:warning",
      "via": "impact_seed:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:dependency:warning"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:function:AnthropicModel",
      "via": "impact_seed:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:function:AnthropicModel"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:function:AnthropicProvider",
      "via": "impact_seed:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:function:AnthropicProvider"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/provider/provider_service.py:function:OpenAIModel",
      "via": "impact_seed:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "exception_flow"
      ],
      "propagation_path": [
        "seed:app/modules/intelligence/provider/provider_service.py:function:OpenAIModel"
      ],
      "propagation_depth": 0,
      "propagation_type": "data_flow",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "focus",
      "id": "focus:branch_coverage",
      "via": "propagated_from:app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "data_processing",
        "exception_flow"
      ],
      "propagation_path": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
        "focus:branch_coverage"
      ],
      "propagation_depth": 1,
      "propagation_type": "test_focus",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "focus",
      "id": "focus:conditional_render",
      "via": "propagated_from:app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "data_processing",
        "exception_flow"
      ],
      "propagation_path": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
        "focus:conditional_render"
      ],
      "propagation_depth": 1,
      "propagation_type": "test_focus",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "focus",
      "id": "focus:dependency_stub",
      "via": "propagated_from:app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "config",
        "data_processing",
        "exception_flow"
      ],
      "propagation_path": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
        "focus:dependency_stub"
      ],
      "propagation_depth": 1,
      "propagation_type": "test_focus",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "focus",
      "id": "focus:integration",
      "via": "propagated_from:app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "config",
        "data_processing",
        "exception_flow"
      ],
      "propagation_path": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
        "focus:integration"
      ],
      "propagation_depth": 1,
      "propagation_type": "test_focus",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "focus",
      "id": "focus:interaction",
      "via": "propagated_from:app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "config",
        "data_processing",
        "exception_flow"
      ],
      "propagation_path": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
        "focus:interaction"
      ],
      "propagation_depth": 1,
      "propagation_type": "test_focus",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "focus",
      "id": "focus:side_effects",
      "via": "propagated_from:app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "config",
        "data_processing",
        "exception_flow"
      ],
      "propagation_path": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
        "focus:side_effects"
      ],
      "propagation_depth": 1,
      "propagation_type": "test_focus",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "focus",
      "id": "focus:state_transition",
      "via": "propagated_from:app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
      "depth": 1,
      "impact_type": [
        "data_processing",
        "exception_flow"
      ],
      "propagation_path": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
        "focus:state_transition"
      ],
      "propagation_depth": 1,
      "propagation_type": "test_focus",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "focus",
      "id": "focus:error_paths",
      "via": "propagated_from:app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "focus:error_paths"
      ],
      "propagation_depth": 1,
      "propagation_type": "test_focus",
      "meta": {
        "frequency_hits": 44
      }
    },
    {
      "kind": "focus",
      "id": "focus:exception_assertions",
      "via": "propagated_from:app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "focus:exception_assertions"
      ],
      "propagation_depth": 1,
      "propagation_type": "test_focus",
      "meta": {
        "frequency_hits": 44
      }
    },
    {
      "kind": "focus",
      "id": "focus:resilience",
      "via": "propagated_from:app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "focus:resilience"
      ],
      "propagation_depth": 1,
      "propagation_type": "test_focus",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "focus",
      "id": "focus:boundary_values",
      "via": "propagated_from:app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
      "depth": 1,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
        "focus:boundary_values"
      ],
      "propagation_depth": 1,
      "propagation_type": "test_focus",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "focus",
      "id": "focus:invalid_input",
      "via": "propagated_from:app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
      "depth": 1,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
        "focus:invalid_input"
      ],
      "propagation_depth": 1,
      "propagation_type": "test_focus",
      "meta": {
        "frequency_hits": 15
      }
    },
    {
      "kind": "focus",
      "id": "focus:rejection_behavior",
      "via": "propagated_from:app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
      "depth": 1,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
        "focus:rejection_behavior"
      ],
      "propagation_depth": 1,
      "propagation_type": "test_focus",
      "meta": {
        "frequency_hits": 1
      }
    },
    {
      "kind": "focus",
      "id": "focus:env_missing",
      "via": "derived_test_focus:.env",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        ".env",
        "focus:env_missing"
      ],
      "propagation_depth": 1,
      "propagation_type": "test_focus",
      "meta": {
        "frequency_hits": 21
      }
    },
    {
      "kind": "focus",
      "id": "focus:fallback",
      "via": "derived_test_focus:.env",
      "depth": 1,
      "impact_type": [
        "config",
        "exception_flow"
      ],
      "propagation_path": [
        ".env",
        "focus:fallback"
      ],
      "propagation_depth": 1,
      "propagation_type": "test_focus",
      "meta": {
        "frequency_hits": 21
      }
    },
    {
      "kind": "focus",
      "id": "focus:boundary",
      "via": "derived_test_focus:app/modules/intelligence/provider/llm_config.py",
      "depth": 1,
      "impact_type": [
        "data_processing"
      ],
      "propagation_path": [
        "app/modules/intelligence/provider/llm_config.py",
        "focus:boundary"
      ],
      "propagation_depth": 1,
      "propagation_type": "test_focus",
      "meta": {
        "frequency_hits": 14
      }
    }
  ],
  "impacted_ranked": [
    {
      "kind": "file",
      "id": "app/modules/intelligence/myprovider_client.py",
      "score": 1.0,
      "reason": "changed_file | path=[app/modules/intelligence/myprovider_client.py] | prop_type=call | types=[config,exception_flow] | product(decay=1.000,dep=1.30)=0.766; after_graph_boost=0.986; prop_depth=0; prop_type=call",
      "test_strategy": [
        {
          "type": "env_missing_fallback",
          "target": "app/modules/intelligence/myprovider_client.py",
          "priority": 0.92
        },
        {
          "type": "exception_assertion",
          "target": "app/modules/intelligence/myprovider_client.py",
          "priority": 0.93
        }
      ],
      "system_impact": [
        "configuration_system",
        "fallback_mechanism",
        "multimodal_pipeline"
      ],
      "initial_score": 1.0,
      "impact_type": [
        "config",
        "exception_flow"
      ]
    },
    {
      "kind": "file",
      "id": "app/modules/intelligence/provider/provider_service.py",
      "score": 1.0,
      "reason": "changed_file | path=[app/modules/intelligence/provider/provider_service.py] | prop_type=call | types=[exception_flow] | product(decay=1.000,dep=1.30)=0.766; after_graph_boost=0.986; prop_depth=0; prop_type=call",
      "test_strategy": [
        {
          "type": "exception_assertion",
          "target": "app/modules/intelligence/provider/provider_service.py",
          "priority": 0.93
        }
      ],
      "system_impact": [
        "configuration_system",
        "fallback_mechanism",
        "multimodal_pipeline"
      ],
      "initial_score": 1.0,
      "impact_type": [
        "exception_flow"
      ]
    },
    {
      "kind": "symbol",
      "id": "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
      "score": 1.0,
      "reason": "changed_entity | path=[app/modules/intelligence/myprovider_client.py:class:MyProviderClient] | prop_type=exception | types=[config,exception_flow] | product(decay=1.000,dep=1.30)=1.000; after_graph_boost=1.000; prop_depth=0; prop_type=exception",
      "test_strategy": [
        {
          "type": "env_missing_fallback",
          "target": "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
          "priority": 0.92
        },
        {
          "type": "exception_assertion",
          "target": "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
          "priority": 0.93
        }
      ],
      "system_impact": [
        "configuration_system",
        "fallback_mechanism",
        "multimodal_pipeline"
      ],
      "initial_score": 1.0,
      "impact_type": [
        "config",
        "exception_flow"
      ]
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:_stream_request",
      "score": 1.0,
      "reason": "impact_seed:MyProviderClient | path=[seed:app/modules/intelligence/myprovider_client.py:dependency:_stream_request] | prop_type=data_flow | types=[config,exception_flow] | product(decay=1.000,dep=1.30)=0.766; after_graph_boost=0.966; prop_depth=0; prop_type=data_flow",
      "test_strategy": [
        {
          "type": "env_missing_fallback",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:_stream_request",
          "priority": 0.92
        },
        {
          "type": "exception_assertion",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:_stream_request",
          "priority": 0.93
        }
      ],
      "system_impact": [
        "configuration_system",
        "fallback_mechanism",
        "multimodal_pipeline"
      ],
      "initial_score": 1.0,
      "impact_type": [
        "config",
        "exception_flow"
      ]
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:getenv",
      "score": 1.0,
      "reason": "impact_seed:MyProviderClient | path=[seed:app/modules/intelligence/myprovider_client.py:dependency:getenv] | prop_type=config | types=[config,exception_flow] | product(decay=1.000,dep=1.30)=0.766; after_graph_boost=0.966; prop_depth=0; prop_type=config",
      "test_strategy": [
        {
          "type": "env_missing_fallback",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:getenv",
          "priority": 0.92
        },
        {
          "type": "exception_assertion",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:getenv",
          "priority": 0.93
        }
      ],
      "system_impact": [
        "configuration_system",
        "fallback_mechanism",
        "multimodal_pipeline"
      ],
      "initial_score": 1.0,
      "impact_type": [
        "config",
        "exception_flow"
      ]
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:iter_lines",
      "score": 1.0,
      "reason": "impact_seed:MyProviderClient | path=[seed:app/modules/intelligence/myprovider_client.py:dependency:iter_lines] | prop_type=data_flow | types=[config,exception_flow] | product(decay=1.000,dep=1.30)=0.740; after_graph_boost=0.863; prop_depth=0; prop_type=data_flow",
      "test_strategy": [
        {
          "type": "env_missing_fallback",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:iter_lines",
          "priority": 0.92
        },
        {
          "type": "exception_assertion",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:iter_lines",
          "priority": 0.93
        }
      ],
      "system_impact": [
        "configuration_system",
        "fallback_mechanism",
        "multimodal_pipeline"
      ],
      "initial_score": 1.0,
      "impact_type": [
        "config",
        "exception_flow"
      ]
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:json",
      "score": 1.0,
      "reason": "impact_seed:MyProviderClient | path=[seed:app/modules/intelligence/myprovider_client.py:dependency:json] | prop_type=data_flow | types=[config,exception_flow] | product(decay=1.000,dep=1.30)=0.766; after_graph_boost=0.966; prop_depth=0; prop_type=data_flow",
      "test_strategy": [
        {
          "type": "env_missing_fallback",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:json",
          "priority": 0.92
        },
        {
          "type": "exception_assertion",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:json",
          "priority": 0.93
        }
      ],
      "system_impact": [
        "configuration_system",
        "fallback_mechanism",
        "multimodal_pipeline"
      ],
      "initial_score": 1.0,
      "impact_type": [
        "config",
        "exception_flow"
      ]
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:loads",
      "score": 1.0,
      "reason": "impact_seed:MyProviderClient | path=[seed:app/modules/intelligence/myprovider_client.py:dependency:loads] | prop_type=data_flow | types=[config,exception_flow] | product(decay=1.000,dep=1.30)=0.740; after_graph_boost=0.863; prop_depth=0; prop_type=data_flow",
      "test_strategy": [
        {
          "type": "env_missing_fallback",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:loads",
          "priority": 0.92
        },
        {
          "type": "exception_assertion",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:loads",
          "priority": 0.93
        }
      ],
      "system_impact": [
        "configuration_system",
        "fallback_mechanism",
        "multimodal_pipeline"
      ],
      "initial_score": 1.0,
      "impact_type": [
        "config",
        "exception_flow"
      ]
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:post",
      "score": 1.0,
      "reason": "impact_seed:MyProviderClient | path=[seed:app/modules/intelligence/myprovider_client.py:dependency:post] | prop_type=data_flow | types=[config,exception_flow] | product(decay=1.000,dep=1.30)=0.766; after_graph_boost=0.966; prop_depth=0; prop_type=data_flow",
      "test_strategy": [
        {
          "type": "env_missing_fallback",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:post",
          "priority": 0.92
        },
        {
          "type": "exception_assertion",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:post",
          "priority": 0.93
        }
      ],
      "system_impact": [
        "configuration_system",
        "fallback_mechanism",
        "multimodal_pipeline"
      ],
      "initial_score": 1.0,
      "impact_type": [
        "config",
        "exception_flow"
      ]
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:raise_for_status",
      "score": 1.0,
      "reason": "impact_seed:MyProviderClient | path=[seed:app/modules/intelligence/myprovider_client.py:dependency:raise_for_status] | prop_type=data_flow | types=[config,exception_flow] | product(decay=1.000,dep=1.30)=0.766; after_graph_boost=0.966; prop_depth=0; prop_type=data_flow",
      "test_strategy": [
        {
          "type": "env_missing_fallback",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:raise_for_status",
          "priority": 0.92
        },
        {
          "type": "exception_assertion",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:raise_for_status",
          "priority": 0.93
        }
      ],
      "system_impact": [
        "configuration_system",
        "fallback_mechanism",
        "multimodal_pipeline"
      ],
      "initial_score": 1.0,
      "impact_type": [
        "config",
        "exception_flow"
      ]
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:rstrip",
      "score": 1.0,
      "reason": "impact_seed:MyProviderClient | path=[seed:app/modules/intelligence/myprovider_client.py:dependency:rstrip] | prop_type=data_flow | types=[config,exception_flow] | product(decay=1.000,dep=1.30)=0.740; after_graph_boost=0.863; prop_depth=0; prop_type=data_flow",
      "test_strategy": [
        {
          "type": "env_missing_fallback",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:rstrip",
          "priority": 0.92
        },
        {
          "type": "exception_assertion",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:rstrip",
          "priority": 0.93
        }
      ],
      "system_impact": [
        "configuration_system",
        "fallback_mechanism",
        "multimodal_pipeline"
      ],
      "initial_score": 1.0,
      "impact_type": [
        "config",
        "exception_flow"
      ]
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:split",
      "score": 1.0,
      "reason": "impact_seed:MyProviderClient | path=[seed:app/modules/intelligence/myprovider_client.py:dependency:split] | prop_type=data_flow | types=[config,exception_flow] | product(decay=1.000,dep=1.30)=0.766; after_graph_boost=0.966; prop_depth=0; prop_type=data_flow",
      "test_strategy": [
        {
          "type": "env_missing_fallback",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:split",
          "priority": 0.92
        },
        {
          "type": "exception_assertion",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:split",
          "priority": 0.93
        }
      ],
      "system_impact": [
        "configuration_system",
        "fallback_mechanism",
        "multimodal_pipeline"
      ],
      "initial_score": 1.0,
      "impact_type": [
        "config",
        "exception_flow"
      ]
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:startswith",
      "score": 1.0,
      "reason": "impact_seed:MyProviderClient | path=[seed:app/modules/intelligence/myprovider_client.py:dependency:startswith] | prop_type=data_flow | types=[config,exception_flow] | product(decay=1.000,dep=1.30)=0.766; after_graph_boost=0.966; prop_depth=0; prop_type=data_flow",
      "test_strategy": [
        {
          "type": "env_missing_fallback",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:startswith",
          "priority": 0.92
        },
        {
          "type": "exception_assertion",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:startswith",
          "priority": 0.93
        }
      ],
      "system_impact": [
        "configuration_system",
        "fallback_mechanism",
        "multimodal_pipeline"
      ],
      "initial_score": 1.0,
      "impact_type": [
        "config",
        "exception_flow"
      ]
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:strip",
      "score": 1.0,
      "reason": "impact_seed:MyProviderClient | path=[seed:app/modules/intelligence/myprovider_client.py:dependency:strip] | prop_type=data_flow | types=[config,exception_flow] | product(decay=1.000,dep=1.30)=0.766; after_graph_boost=0.966; prop_depth=0; prop_type=data_flow",
      "test_strategy": [
        {
          "type": "env_missing_fallback",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:strip",
          "priority": 0.92
        },
        {
          "type": "exception_assertion",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:strip",
          "priority": 0.93
        }
      ],
      "system_impact": [
        "configuration_system",
        "fallback_mechanism",
        "multimodal_pipeline"
      ],
      "initial_score": 1.0,
      "impact_type": [
        "config",
        "exception_flow"
      ]
    },
    {
      "kind": "seed",
      "id": "seed:app/modules/intelligence/myprovider_client.py:dependency:time",
      "score": 1.0,
      "reason": "impact_seed:MyProviderClient | path=[seed:app/modules/intelligence/myprovider_client.py:dependency:time] | prop_type=data_flow | types=[config,exception_flow] | product(decay=1.000,dep=1.30)=0.766; after_graph_boost=0.966; prop_depth=0; prop_type=data_flow",
      "test_strategy": [
        {
          "type": "env_missing_fallback",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:time",
          "priority": 0.92
        },
        {
          "type": "exception_assertion",
          "target": "seed:app/modules/intelligence/myprovider_client.py:dependency:time",
          "priority": 0.93
        }
      ],
      "system_impact": [
        "configuration_system",
        "fallback_mechanism",
        "multimodal_pipeline"
      ],
      "initial_score": 1.0,
      "impact_type": [
        "config",
        "exception_flow"
      ]
    }
  ],
  "debug": {
    "diff_stats": {
      "files": 6,
      "added": 104,
      "removed": 101
    },
    "change_graph": {
      "node_count": 73,
      "edge_count": 106
    },
    "code_change": {
      "files_analyzed": 6,
      "changes": 5,
      "used_llm": true,
      "llm_refine_files_invoked": 0,
      "llm_refine_files_skipped": 0,
      "cache_hits": 3,
      "cache_misses": 0,
      "cache_writes": 0,
      "elapsed_seconds": 0.014
    },
    "impact": {
      "candidate_count": 76,
      "ranked_count": 15,
      "used_llm": true,
      "change_graph_used": true,
      "propagation_hops_max": 3,
      "base_candidate_count": 60,
      "propagated_candidate_count": 2325,
      "synthetic_focus_candidate_count": 156,
      "test_focus_count": 16,
      "impact_type_distribution": {
        "exception_flow": 55,
        "config": 30,
        "data_processing": 25
      },
      "ranking_mode": "llm_error_fallback",
      "llm_error": "JSONDecodeError: Expecting ',' delimiter: line 503 column 18 (char 16999)",
      "elapsed_seconds": 121.489
    }
  }
}

改进语句：
你是一个资深 Python 架构工程师，请帮我重构 ImpactAgent 的输出结构。

## 🎯 改造目标（必须满足）

当前 Impact 分析结果存在以下问题：
1. 节点粒度过细（大量 dependency / builtin function 噪声）
2. 所有节点 score 几乎为 1.0，无法排序
3. file / symbol / seed 混在一起，没有层级结构
4. test_focus 是拍脑袋生成，没有规则来源
5. test_strategy 太抽象，无法直接生成测试用例

请你基于这些问题，对当前 ImpactAgent 做“结构性重构”，而不是局部修改。

---

## 🧠 目标输出结构（必须按这个设计）

请将当前结构：

impacted → 平铺节点列表

改为：

{
  "impact_graph": [
    {
      "file": "...",
      "symbols": [
        {
          "name": "...",
          "semantic_units": [
            {
              "type": "config | exception | api | data_processing",
              "source": "...",
              "risk_score": 0.xx,
              "test_focus": [
                {
                  "type": "...",
                  "derived_from": "规则说明"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}

---

## ✂️ 关键改造要求

### 1. 做“语义剪枝”
删除以下节点：
- dependency: split / strip / startswith / json / loads 等
- Python 内置函数
- 无业务语义的变量

改为聚合成：
- ConfigAccess（如 getenv / .env）
- ExceptionFlow（raise / ValueError）
- ExternalAPI（requests.post）
- DataProcessing

---

### 2. 引入层级结构
必须分层：
- file
- symbol（class / method）
- semantic_unit（语义单元）

禁止再出现平铺的 impacted 列表

---

### 3. 重写 scoring 逻辑

score 不能全是 1.0，必须实现：

score =
  change_weight × propagation_decay × semantic_weight × risk_weight

要求：
- config / exception 权重更高
- 字符串处理权重降低
- propagation depth 越深，分数越低

---

### 4. test_focus 必须规则驱动

不要随机生成 focus，必须基于规则：

例如：
- config → env_missing / fallback
- exception → error_paths / exception_assertion
- api → retry / timeout / mock

输出必须包含：
"derived_from": "规则说明"

---

### 5. test_strategy 改成可执行结构

不要再输出：
"type": "exception_assertion"

必须改为：

{
  "scenario": "...",
  "input": "...",
  "mock": "...",
  "assert": "..."
}

---

## 📌 额外要求

- 保留现有代码结构，尽量在 ImpactAgent 内重构
- 输出一个示例 JSON（基于当前输入数据）
- 代码要清晰、模块化（可以拆函数）
- 给出关键函数说明（用中文注释）

---

## 🚀 目标

让 ImpactAgent 的输出可以被 TestPlanningAgent 直接消费，
而不是再做二次解析。


改进后：
{
  "repo_path": "/Users/admin/Desktop/potpie_bge",
  "changed_files": [
    ".env",
    ".env.template",
    "app/modules/intelligence/myprovider_client.py",
    "app/modules/intelligence/provider/llm_config.py",
    "app/modules/intelligence/provider/provider_service.py",
    "potpie-ui/.env"
  ],
  "impact_graph": [
    {
      "file": "app/modules/intelligence/myprovider_client.py",
      "symbols": [
        {
          "name": "MyProviderClient",
          "entity_type": "class",
          "symbol_id": "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
          "semantic_units": [
            {
              "type": "api",
              "source": "seed:dependency:_stream_request; seed:dependency:iter_lines; seed:dependency:post; seed:dependency:rstrip; seed:dependency:time; semantic_tag→api",
              "risk_score": 0.4541,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "retry",
                  "derived_from": "规则：type=api → 覆盖重试与退避"
                },
                {
                  "type": "timeout",
                  "derived_from": "规则：type=api → 覆盖超时行为"
                },
                {
                  "type": "mock",
                  "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "MyProviderClient 外部 HTTP/API 失败（5xx/网络错误）",
                  "input": "构造会导致失败的请求参数或 URL",
                  "mock": "使用 responses/httpx.MockTransport 模拟 500 或连接错误",
                  "assert": "应重试（若实现有）或在达到上限后失败；不得无限阻塞"
                },
                {
                  "scenario": "MyProviderClient 请求超时",
                  "input": "正常参数",
                  "mock": "模拟长时间无响应或 timeout 异常",
                  "assert": "应在约定时间内失败并暴露可测试的超时错误"
                }
              ]
            },
            {
              "type": "config",
              "source": "seed:dependency:getenv",
              "risk_score": 0.4897,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "env_missing",
                  "derived_from": "规则：type=config → 覆盖环境变量缺失"
                },
                {
                  "type": "fallback",
                  "derived_from": "规则：type=config → 覆盖默认值 / 配置回退"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "未设置相关环境变量时 MyProviderClient 的配置解析行为",
                  "input": "清除目标环境变量（或在隔离进程中未注入该变量）",
                  "mock": "使用 monkeypatch.delenv 或 patch 掉 os.environ / 配置加载函数",
                  "assert": "应回退到文档约定的默认值，或抛出明确的配置错误（与产品行为一致）"
                },
                {
                  "scenario": "配置项非法或类型错误时 MyProviderClient 的容错",
                  "input": "注入类型错误或越界配置值",
                  "mock": "patch 配置源返回非法值",
                  "assert": "应拒绝启动或记录可观测错误，不应静默吞掉"
                }
              ]
            },
            {
              "type": "exception",
              "source": "seed:dependency:raise_for_status; semantic_tag→exception",
              "risk_score": 0.5075,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "error_paths",
                  "derived_from": "规则：type=exception → 覆盖错误分支与非法输入"
                },
                {
                  "type": "exception_assertion",
                  "derived_from": "规则：type=exception → 断言异常类型与信息"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "对 MyProviderClient 传入非法/空输入",
                  "input": "None、空字符串、越界索引等（按签名选择）",
                  "mock": "无需网络；必要时 patch 下游为抛错",
                  "assert": "应抛出与实现一致的异常类型（如 ValueError/TypeError），信息可读"
                },
                {
                  "scenario": "MyProviderClient 依赖路径失败时的异常路径",
                  "input": "触发内部校验失败分支",
                  "mock": "patch 依赖调用返回失败或抛异常",
                  "assert": "异常向上传播或被捕获后转为业务错误码/消息"
                }
              ]
            }
          ]
        },
        {
          "name": "create_chat_completion",
          "entity_type": "method",
          "symbol_id": "app/modules/intelligence/myprovider_client.py:method:create_chat_completion",
          "semantic_units": [
            {
              "type": "api",
              "source": "seed:dependency:_stream_request; seed:dependency:post; seed:dependency:time; semantic_tag→api",
              "risk_score": 0.4541,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "retry",
                  "derived_from": "规则：type=api → 覆盖重试与退避"
                },
                {
                  "type": "timeout",
                  "derived_from": "规则：type=api → 覆盖超时行为"
                },
                {
                  "type": "mock",
                  "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "create_chat_completion 外部 HTTP/API 失败（5xx/网络错误）",
                  "input": "构造会导致失败的请求参数或 URL",
                  "mock": "使用 responses/httpx.MockTransport 模拟 500 或连接错误",
                  "assert": "应重试（若实现有）或在达到上限后失败；不得无限阻塞"
                },
                {
                  "scenario": "create_chat_completion 请求超时",
                  "input": "正常参数",
                  "mock": "模拟长时间无响应或 timeout 异常",
                  "assert": "应在约定时间内失败并暴露可测试的超时错误"
                }
              ]
            },
            {
              "type": "config",
              "source": "seed:dependency:getenv",
              "risk_score": 0.4897,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "env_missing",
                  "derived_from": "规则：type=config → 覆盖环境变量缺失"
                },
                {
                  "type": "fallback",
                  "derived_from": "规则：type=config → 覆盖默认值 / 配置回退"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "未设置相关环境变量时 create_chat_completion 的配置解析行为",
                  "input": "清除目标环境变量（或在隔离进程中未注入该变量）",
                  "mock": "使用 monkeypatch.delenv 或 patch 掉 os.environ / 配置加载函数",
                  "assert": "应回退到文档约定的默认值，或抛出明确的配置错误（与产品行为一致）"
                },
                {
                  "scenario": "配置项非法或类型错误时 create_chat_completion 的容错",
                  "input": "注入类型错误或越界配置值",
                  "mock": "patch 配置源返回非法值",
                  "assert": "应拒绝启动或记录可观测错误，不应静默吞掉"
                }
              ]
            },
            {
              "type": "exception",
              "source": "seed:dependency:raise_for_status; seed:variable:Exception; seed:variable:ValueError; semantic_tag→exception",
              "risk_score": 0.5075,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "error_paths",
                  "derived_from": "规则：type=exception → 覆盖错误分支与非法输入"
                },
                {
                  "type": "exception_assertion",
                  "derived_from": "规则：type=exception → 断言异常类型与信息"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "对 create_chat_completion 传入非法/空输入",
                  "input": "None、空字符串、越界索引等（按签名选择）",
                  "mock": "无需网络；必要时 patch 下游为抛错",
                  "assert": "应抛出与实现一致的异常类型（如 ValueError/TypeError），信息可读"
                },
                {
                  "scenario": "create_chat_completion 依赖路径失败时的异常路径",
                  "input": "触发内部校验失败分支",
                  "mock": "patch 依赖调用返回失败或抛异常",
                  "assert": "异常向上传播或被捕获后转为业务错误码/消息"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "file": "app/modules/intelligence/provider/llm_config.py",
      "symbols": [
        {
          "name": "get_config_for_model",
          "entity_type": "function",
          "symbol_id": "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
          "semantic_units": [
            {
              "type": "api",
              "source": "seed:dependency:get; semantic_tag→api",
              "risk_score": 0.3495,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "retry",
                  "derived_from": "规则：type=api → 覆盖重试与退避"
                },
                {
                  "type": "timeout",
                  "derived_from": "规则：type=api → 覆盖超时行为"
                },
                {
                  "type": "mock",
                  "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "get_config_for_model 外部 HTTP/API 失败（5xx/网络错误）",
                  "input": "构造会导致失败的请求参数或 URL",
                  "mock": "使用 responses/httpx.MockTransport 模拟 500 或连接错误",
                  "assert": "应重试（若实现有）或在达到上限后失败；不得无限阻塞"
                },
                {
                  "scenario": "get_config_for_model 请求超时",
                  "input": "正常参数",
                  "mock": "模拟长时间无响应或 timeout 异常",
                  "assert": "应在约定时间内失败并暴露可测试的超时错误"
                }
              ]
            },
            {
              "type": "data_processing",
              "source": "seed:function:parse_model_string; seed:variable:Any; seed:variable:MODEL_CONFIG_MAP; seed:variable:fallback_auth_provider; seed:variable:model_string; seed:variable:os; seed:variable:parse_model_string; seed:variable:provider; semantic_tag→data_processing",
              "risk_score": 0.2604,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "boundary",
                  "derived_from": "规则：type=data_processing → 边界值与空输入"
                },
                {
                  "type": "invalid_input",
                  "derived_from": "规则：type=data_processing → 非法格式/解析失败"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "get_config_for_model 解析/校验输入数据（app/modules/intelligence/provider/llm_config.py::get_config_for_model）",
                  "input": "合法边界值、空集合、畸形字符串（如非法 JSON 片段）",
                  "mock": "必要时隔离文件/网络数据源",
                  "assert": "合法输入通过；非法输入抛出解析错误或返回显式错误状态"
                }
              ]
            },
            {
              "type": "config",
              "source": "seed:variable:env_base_url; seed:variable:fallback_base_url",
              "risk_score": 0.3769,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "env_missing",
                  "derived_from": "规则：type=config → 覆盖环境变量缺失"
                },
                {
                  "type": "fallback",
                  "derived_from": "规则：type=config → 覆盖默认值 / 配置回退"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "未设置相关环境变量时 get_config_for_model 的配置解析行为",
                  "input": "清除目标环境变量（或在隔离进程中未注入该变量）",
                  "mock": "使用 monkeypatch.delenv 或 patch 掉 os.environ / 配置加载函数",
                  "assert": "应回退到文档约定的默认值，或抛出明确的配置错误（与产品行为一致）"
                },
                {
                  "scenario": "配置项非法或类型错误时 get_config_for_model 的容错",
                  "input": "注入类型错误或越界配置值",
                  "mock": "patch 配置源返回非法值",
                  "assert": "应拒绝启动或记录可观测错误，不应静默吞掉"
                }
              ]
            },
            {
              "type": "exception",
              "source": "semantic_tag→exception",
              "risk_score": 0.3906,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "error_paths",
                  "derived_from": "规则：type=exception → 覆盖错误分支与非法输入"
                },
                {
                  "type": "exception_assertion",
                  "derived_from": "规则：type=exception → 断言异常类型与信息"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "对 get_config_for_model 传入非法/空输入",
                  "input": "None、空字符串、越界索引等（按签名选择）",
                  "mock": "无需网络；必要时 patch 下游为抛错",
                  "assert": "应抛出与实现一致的异常类型（如 ValueError/TypeError），信息可读"
                },
                {
                  "scenario": "get_config_for_model 依赖路径失败时的异常路径",
                  "input": "触发内部校验失败分支",
                  "mock": "patch 依赖调用返回失败或抛异常",
                  "assert": "异常向上传播或被捕获后转为业务错误码/消息"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "file": "app/modules/intelligence/provider/provider_service.py",
      "symbols": [
        {
          "name": "ProviderService",
          "entity_type": "class",
          "symbol_id": "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
          "semantic_units": [
            {
              "type": "api",
              "source": "seed:dependency:_build_config_for_model_identifier; seed:dependency:_build_llm_params; seed:dependency:_format_anthropic_multimodal_message; seed:dependency:_format_gemini_multimodal_message; seed:dependency:_format_multimodal_message; seed:dependency:_format_multimodal_messages; seed:dependency:_format_openai_multimodal_message; seed:dependency:add; seed:dependency:append; seed:dependency:call_llm; semantic_tag→api",
              "risk_score": 0.4723,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "retry",
                  "derived_from": "规则：type=api → 覆盖重试与退避"
                },
                {
                  "type": "timeout",
                  "derived_from": "规则：type=api → 覆盖超时行为"
                },
                {
                  "type": "mock",
                  "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "ProviderService 外部 HTTP/API 失败（5xx/网络错误）",
                  "input": "构造会导致失败的请求参数或 URL",
                  "mock": "使用 responses/httpx.MockTransport 模拟 500 或连接错误",
                  "assert": "应重试（若实现有）或在达到上限后失败；不得无限阻塞"
                },
                {
                  "scenario": "ProviderService 请求超时",
                  "input": "正常参数",
                  "mock": "模拟长时间无响应或 timeout 异常",
                  "assert": "应在约定时间内失败并暴露可测试的超时错误"
                }
              ]
            },
            {
              "type": "config",
              "source": "seed:dependency:_get_api_key",
              "risk_score": 0.5093,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "env_missing",
                  "derived_from": "规则：type=config → 覆盖环境变量缺失"
                },
                {
                  "type": "fallback",
                  "derived_from": "规则：type=config → 覆盖默认值 / 配置回退"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "未设置相关环境变量时 ProviderService 的配置解析行为",
                  "input": "清除目标环境变量（或在隔离进程中未注入该变量）",
                  "mock": "使用 monkeypatch.delenv 或 patch 掉 os.environ / 配置加载函数",
                  "assert": "应回退到文档约定的默认值，或抛出明确的配置错误（与产品行为一致）"
                },
                {
                  "scenario": "配置项非法或类型错误时 ProviderService 的容错",
                  "input": "注入类型错误或越界配置值",
                  "mock": "patch 配置源返回非法值",
                  "assert": "应拒绝启动或记录可观测错误，不应静默吞掉"
                }
              ]
            },
            {
              "type": "data_processing",
              "source": "seed:dependency:_validate_images_for_multimodal; semantic_tag→data_processing",
              "risk_score": 0.3519,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "boundary",
                  "derived_from": "规则：type=data_processing → 边界值与空输入"
                },
                {
                  "type": "invalid_input",
                  "derived_from": "规则：type=data_processing → 非法格式/解析失败"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "ProviderService 解析/校验输入数据（app/modules/intelligence/provider/provider_service.py::ProviderService）",
                  "input": "合法边界值、空集合、畸形字符串（如非法 JSON 片段）",
                  "mock": "必要时隔离文件/网络数据源",
                  "assert": "合法输入通过；非法输入抛出解析错误或返回显式错误状态"
                }
              ]
            },
            {
              "type": "exception",
              "source": "semantic_tag→exception",
              "risk_score": 0.5278,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "error_paths",
                  "derived_from": "规则：type=exception → 覆盖错误分支与非法输入"
                },
                {
                  "type": "exception_assertion",
                  "derived_from": "规则：type=exception → 断言异常类型与信息"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "对 ProviderService 传入非法/空输入",
                  "input": "None、空字符串、越界索引等（按签名选择）",
                  "mock": "无需网络；必要时 patch 下游为抛错",
                  "assert": "应抛出与实现一致的异常类型（如 ValueError/TypeError），信息可读"
                },
                {
                  "scenario": "ProviderService 依赖路径失败时的异常路径",
                  "input": "触发内部校验失败分支",
                  "mock": "patch 依赖调用返回失败或抛异常",
                  "assert": "异常向上传播或被捕获后转为业务错误码/消息"
                }
              ]
            }
          ]
        },
        {
          "name": "get_pydantic_model",
          "entity_type": "method",
          "symbol_id": "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
          "semantic_units": [
            {
              "type": "api",
              "source": "seed:dependency:_build_config_for_model_identifier; seed:dependency:get; seed:dependency:items; seed:dependency:rstrip; seed:dependency:warning; semantic_tag→api",
              "risk_score": 0.4455,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "retry",
                  "derived_from": "规则：type=api → 覆盖重试与退避"
                },
                {
                  "type": "timeout",
                  "derived_from": "规则：type=api → 覆盖超时行为"
                },
                {
                  "type": "mock",
                  "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "get_pydantic_model 外部 HTTP/API 失败（5xx/网络错误）",
                  "input": "构造会导致失败的请求参数或 URL",
                  "mock": "使用 responses/httpx.MockTransport 模拟 500 或连接错误",
                  "assert": "应重试（若实现有）或在达到上限后失败；不得无限阻塞"
                },
                {
                  "scenario": "get_pydantic_model 请求超时",
                  "input": "正常参数",
                  "mock": "模拟长时间无响应或 timeout 异常",
                  "assert": "应在约定时间内失败并暴露可测试的超时错误"
                }
              ]
            },
            {
              "type": "config",
              "source": "seed:dependency:_get_api_key",
              "risk_score": 0.4805,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "env_missing",
                  "derived_from": "规则：type=config → 覆盖环境变量缺失"
                },
                {
                  "type": "fallback",
                  "derived_from": "规则：type=config → 覆盖默认值 / 配置回退"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "未设置相关环境变量时 get_pydantic_model 的配置解析行为",
                  "input": "清除目标环境变量（或在隔离进程中未注入该变量）",
                  "mock": "使用 monkeypatch.delenv 或 patch 掉 os.environ / 配置加载函数",
                  "assert": "应回退到文档约定的默认值，或抛出明确的配置错误（与产品行为一致）"
                },
                {
                  "scenario": "配置项非法或类型错误时 get_pydantic_model 的容错",
                  "input": "注入类型错误或越界配置值",
                  "mock": "patch 配置源返回非法值",
                  "assert": "应拒绝启动或记录可观测错误，不应静默吞掉"
                }
              ]
            },
            {
              "type": "data_processing",
              "source": "seed:function:AnthropicModel; seed:function:AnthropicProvider; seed:function:OpenAIModel; semantic_tag→data_processing",
              "risk_score": 0.332,
              "propagation_depth": 0,
              "test_focus": [
                {
                  "type": "boundary",
                  "derived_from": "规则：type=data_processing → 边界值与空输入"
                },
                {
                  "type": "invalid_input",
                  "derived_from": "规则：type=data_processing → 非法格式/解析失败"
                }
              ],
              "test_strategy": [
                {
                  "scenario": "get_pydantic_model 解析/校验输入数据（app/modules/intelligence/provider/provider_service.py::get_pydantic_model）",
                  "input": "合法边界值、空集合、畸形字符串（如非法 JSON 片段）",
                  "mock": "必要时隔离文件/网络数据源",
                  "assert": "合法输入通过；非法输入抛出解析错误或返回显式错误状态"
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "impacted": [],
  "impacted_ranked": [],
  "debug": {
    "diff_stats": {
      "files": 6,
      "added": 104,
      "removed": 101
    },
    "change_graph": {
      "node_count": 73,
      "edge_count": 106
    },
    "code_change": {
      "files_analyzed": 6,
      "changes": 5,
      "used_llm": true,
      "llm_refine_files_invoked": 0,
      "llm_refine_files_skipped": 0,
      "cache_hits": 3,
      "cache_misses": 0,
      "cache_writes": 0,
      "elapsed_seconds": 0.014
    },
    "impact": {
      "mode": "impact_graph_v2",
      "candidate_count": 0,
      "ranked_count": 0,
      "used_llm": false,
      "change_graph_used": true,
      "propagation_hops_max": 3,
      "base_candidate_count": 0,
      "propagated_candidate_count": 0,
      "synthetic_focus_candidate_count": 0,
      "test_focus_count": 39,
      "impact_type_distribution": {
        "api": 5,
        "config": 5,
        "exception": 4,
        "data_processing": 3
      },
      "ranking_mode": "layered_graph",
      "llm_error": null,
      "elapsed_seconds": 0.001,
      "llm_refine_enabled": false,
      "note": "主输出为 state.impact_graph；平铺 impacted 已弃用"
    }
  }
}

改进：
你是一个资深后端架构工程师，请在现有 ImpactAgent V2 的基础上继续重构为 V3。

当前系统已经具备：
- file → symbol → semantic_unit 分层结构
- semantic_unit 已分类为 api / config / exception / data_processing
- 已生成 test_focus 和 test_strategy

但仍存在关键问题，请严格按以下要求升级：

---

# 🎯 目标：从“Impact分析”升级为“Test Planning系统”

---

## ❗问题1：semantic_unit 重复（必须解决）

当前问题：
- class 和 method 中存在重复 semantic_unit（如 api/config/exception）

### ✅ 改造要求：

引入 semantic_unit_id，实现复用机制：

{
  "semantic_unit_id": "api:stream_request",
  "type": "api",
  ...
}

要求：
- 相同语义（如 API调用）只创建一次 semantic_unit
- symbol 中引用 semantic_unit_id，而不是重复定义

---

## ❗问题2：risk_score 无法排序（必须改）

当前问题：
- risk_score 在 0.3~0.5 之间，没有全局意义

### ✅ 改造要求：

新增字段：

"priority_score": float（0~1）

计算规则：

priority_score =
  risk_score
× change_weight（是否直接修改文件：1.0 / 0.7）
× centrality（调用链核心程度：1.2 / 1.0 / 0.8）
× frequency（semantic_unit 被引用次数）

要求：
- 不同 semantic_unit 之间必须能明显拉开差距
- 输出 Top-N 高优先级节点

---

## ❗问题3：缺跨文件调用链（非常重要）

当前问题：
- impact_graph 仅限单文件内部

### ✅ 改造要求：

为 semantic_unit 增加：

"call_chain": [
  "MyProviderClient.create_chat_completion",
  "ProviderService.call_llm",
  "llm_config.get_config_for_model"
]

或：

"downstream": ["..."]

要求：
- 至少支持 1~2 跳跨文件传播
- 标识 integration 风险

---

## ❗问题4：test_strategy 仍然过于通用

当前问题：
- API 测试全部类似（mock 500 / timeout）

### ✅ 改造要求：

引入“语义感知测试生成”：

例如：
- 如果 semantic_unit 包含 "_stream"
  → 生成 streaming 中断测试

- 如果 semantic_unit 包含 "config"
  → 区分 env / fallback / override

- 如果 semantic_unit 包含 "exception"
  → 区分内部异常 / 外部异常

要求：
- test_strategy 必须体现具体函数语义
- 避免所有 API 用同一模板

---

## ❗问题5：缺测试优先级（必须加）

### ✅ 改造要求：

为每个 semantic_unit 添加：

"test_priority": "P0 | P1 | P2"

规则：

- exception + config → P0
- external_api → P0
- data_processing → P1
- 低风险处理 → P2

---

## ❗问题6：输出 Test Plan（核心目标）

在 impact_graph 之外，新增：

"test_plan": [
  {
    "target": "MyProviderClient",
    "priority": "P0",
    "test_types": ["integration", "exception"],
    "estimated_cases": 5,
    "reason": "涉及 API + config + exception"
  }
]

要求：
- 汇总 semantic_unit 生成测试计划
- 用于直接指导测试执行

---

# 📌 输出要求

请输出：

1️⃣ 重构后的 ImpactAgent 核心代码（Python）
2️⃣ 新的输出 JSON 示例（基于当前输入）
3️⃣ 重构说明（重点说明 semantic_unit 复用 + priority_score + test_plan）

---

# 🚀 最终目标

让 ImpactAgent 输出可以：
✔ 直接用于测试优先级排序  
✔ 自动生成测试计划  
✔ 支持跨模块影响分析  

改进后：
{
  "repo_path": "/Users/admin/Desktop/potpie_bge",
  "changed_files": [
    ".env",
    ".env.template",
    "app/modules/intelligence/myprovider_client.py",
    "app/modules/intelligence/provider/llm_config.py",
    "app/modules/intelligence/provider/provider_service.py",
    "potpie-ui/.env"
  ],
  "semantic_units_catalog": [
    {
      "semantic_unit_id": "api:build_config_for_model_identifier_build_llm_params_format_anthropic_multimodal_m",
      "type": "api",
      "source": "seed:dependency:_build_config_for_model_identifier; seed:dependency:_build_llm_params; seed:dependency:_format_anthropic_multimodal_message; seed:dependency:_format_gemini_multimodal_message; seed:dependency:_format_multimodal_message; seed:dependency:_format_multimodal_messages; seed:dependency:_format_openai_multimodal_message; seed:dependency:add; seed:dependency:append; seed:dependency:call_llm; semantic_tag→api",
      "risk_score": 0.4723,
      "priority_score": 0.1984,
      "test_priority": "P0",
      "centrality_factor": 1.0,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "downstream": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "ProviderService：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "ProviderService：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:build_config_for_model_identifier_get_items_rstrip_warning_semantic_tag_api",
      "type": "api",
      "source": "seed:dependency:_build_config_for_model_identifier; seed:dependency:get; seed:dependency:items; seed:dependency:rstrip; seed:dependency:warning; semantic_tag→api",
      "risk_score": 0.4455,
      "priority_score": 0.1984,
      "test_priority": "P0",
      "centrality_factor": 1.2,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "downstream": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "integration_risk": true,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_pydantic_model：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "get_pydantic_model：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:get_semantic_tag_api",
      "type": "api",
      "source": "seed:dependency:get; semantic_tag→api",
      "risk_score": 0.3495,
      "priority_score": 0.1984,
      "test_priority": "P0",
      "centrality_factor": 1.0,
      "call_chain": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "downstream": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "integration_risk": true,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_config_for_model：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "get_config_for_model：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:stream_request_iter_lines_post_rstrip_time_semantic_tag_api",
      "type": "api",
      "source": "seed:dependency:_stream_request; seed:dependency:iter_lines; seed:dependency:post; seed:dependency:rstrip; seed:dependency:time; semantic_tag→api",
      "risk_score": 0.4541,
      "priority_score": 0.1984,
      "test_priority": "P0",
      "centrality_factor": 1.2,
      "call_chain": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion",
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "downstream": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion",
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "integration_risk": true,
      "referenced_symbol_ids": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "MyProviderClient：流式响应中途取消/客户端断开",
          "input": "消费 generator/async iterator 若干 chunk 后关闭",
          "mock": "模拟 client 中断或 asyncio.CancelledError",
          "assert": "资源释放（连接/文件句柄）；无悬挂任务；错误可观测"
        },
        {
          "scenario": "MyProviderClient：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "MyProviderClient：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:stream_request_post_time_semantic_tag_api",
      "type": "api",
      "source": "seed:dependency:_stream_request; seed:dependency:post; seed:dependency:time; semantic_tag→api",
      "risk_score": 0.4541,
      "priority_score": 0.1984,
      "test_priority": "P0",
      "centrality_factor": 1.0,
      "call_chain": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion",
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient"
      ],
      "downstream": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "create_chat_completion：流式响应中途取消/客户端断开",
          "input": "消费 generator/async iterator 若干 chunk 后关闭",
          "mock": "模拟 client 中断或 asyncio.CancelledError",
          "assert": "资源释放（连接/文件句柄）；无悬挂任务；错误可观测"
        },
        {
          "scenario": "create_chat_completion：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "create_chat_completion：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "config:env_base_url_fallback_base_url",
      "type": "config",
      "source": "seed:variable:env_base_url; seed:variable:fallback_base_url",
      "risk_score": 0.3769,
      "priority_score": 0.1984,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "downstream": [],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "env_missing",
          "derived_from": "规则：type=config → 覆盖环境变量缺失"
        },
        {
          "type": "fallback",
          "derived_from": "规则：type=config → 覆盖默认值 / 配置回退"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_config_for_model：显式配置覆盖默认/回退（override 路径）",
          "input": "在同时提供默认值与显式参数/配置文件时调用",
          "mock": "patch 配置源顺序，制造后写覆盖先写",
          "assert": "显式配置优先生效；回退链路与文档一致"
        },
        {
          "scenario": "get_config_for_model：配置项类型或范围非法",
          "input": "注入非数字端口、空 URL、负数超时等",
          "mock": "patch 配置读取返回值",
          "assert": "拒绝非法配置并失败可测，不应静默继续"
        }
      ]
    },
    {
      "semantic_unit_id": "config:get_api_key",
      "type": "config",
      "source": "seed:dependency:_get_api_key",
      "risk_score": 0.5093,
      "priority_score": 0.1984,
      "test_priority": "P0",
      "centrality_factor": 1.0,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "downstream": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "env_missing",
          "derived_from": "规则：type=config → 覆盖环境变量缺失"
        },
        {
          "type": "fallback",
          "derived_from": "规则：type=config → 覆盖默认值 / 配置回退"
        }
      ],
      "test_strategy": [
        {
          "scenario": "ProviderService：显式配置覆盖默认/回退（override 路径）",
          "input": "在同时提供默认值与显式参数/配置文件时调用",
          "mock": "patch 配置源顺序，制造后写覆盖先写",
          "assert": "显式配置优先生效；回退链路与文档一致"
        },
        {
          "scenario": "ProviderService：配置项类型或范围非法",
          "input": "注入非数字端口、空 URL、负数超时等",
          "mock": "patch 配置读取返回值",
          "assert": "拒绝非法配置并失败可测，不应静默继续"
        }
      ]
    },
    {
      "semantic_unit_id": "config:getenv",
      "type": "config",
      "source": "seed:dependency:getenv",
      "risk_score": 0.4897,
      "priority_score": 0.1984,
      "test_priority": "P0",
      "centrality_factor": 1.0,
      "call_chain": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "downstream": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "env_missing",
          "derived_from": "规则：type=config → 覆盖环境变量缺失"
        },
        {
          "type": "fallback",
          "derived_from": "规则：type=config → 覆盖默认值 / 配置回退"
        }
      ],
      "test_strategy": [
        {
          "scenario": "MyProviderClient：未设置关键环境变量时的行为（env 路径）",
          "input": "使用 monkeypatch.delenv 删除约定变量名后调用",
          "mock": "monkeypatch / patch.dict(os.environ, clear=True) 局部清除",
          "assert": "应抛出明确 ConfigurationError/ValueError 或使用文档记载的默认值"
        },
        {
          "scenario": "MyProviderClient：显式配置覆盖默认/回退（override 路径）",
          "input": "在同时提供默认值与显式参数/配置文件时调用",
          "mock": "patch 配置源顺序，制造后写覆盖先写",
          "assert": "显式配置优先生效；回退链路与文档一致"
        }
      ]
    },
    {
      "semantic_unit_id": "data_processing:anthropicmodel_anthropicprovider_openaimodel_semantic_tag_data_processing",
      "type": "data_processing",
      "source": "seed:function:AnthropicModel; seed:function:AnthropicProvider; seed:function:OpenAIModel; semantic_tag→data_processing",
      "risk_score": 0.332,
      "priority_score": 0.1984,
      "test_priority": "P2",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "downstream": [],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "boundary",
          "derived_from": "规则：type=data_processing → 边界值与空输入"
        },
        {
          "type": "invalid_input",
          "derived_from": "规则：type=data_processing → 非法格式/解析失败"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_pydantic_model 数据解析/校验（app/modules/intelligence/provider/provider_service.py::get_pydantic_model）",
          "input": "合法边界、空输入、畸形片段",
          "mock": "隔离文件与网络",
          "assert": "合法通过；非法显式失败"
        }
      ]
    },
    {
      "semantic_unit_id": "data_processing:parse_model_string_any_model_config_map_fallback_auth_provider_model_string_os",
      "type": "data_processing",
      "source": "seed:function:parse_model_string; seed:variable:Any; seed:variable:MODEL_CONFIG_MAP; seed:variable:fallback_auth_provider; seed:variable:model_string; seed:variable:os; seed:variable:parse_model_string; seed:variable:provider; semantic_tag→data_processing",
      "risk_score": 0.2604,
      "priority_score": 0.1984,
      "test_priority": "P2",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "downstream": [],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "boundary",
          "derived_from": "规则：type=data_processing → 边界值与空输入"
        },
        {
          "type": "invalid_input",
          "derived_from": "规则：type=data_processing → 非法格式/解析失败"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_config_for_model 数据解析/校验（app/modules/intelligence/provider/llm_config.py::get_config_for_model）",
          "input": "合法边界、空输入、畸形片段",
          "mock": "隔离文件与网络",
          "assert": "合法通过；非法显式失败"
        }
      ]
    },
    {
      "semantic_unit_id": "data_processing:validate_images_for_multimodal_semantic_tag_data_processing",
      "type": "data_processing",
      "source": "seed:dependency:_validate_images_for_multimodal; semantic_tag→data_processing",
      "risk_score": 0.3519,
      "priority_score": 0.1984,
      "test_priority": "P2",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "downstream": [],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "boundary",
          "derived_from": "规则：type=data_processing → 边界值与空输入"
        },
        {
          "type": "invalid_input",
          "derived_from": "规则：type=data_processing → 非法格式/解析失败"
        }
      ],
      "test_strategy": [
        {
          "scenario": "ProviderService 数据解析/校验（app/modules/intelligence/provider/provider_service.py::ProviderService）",
          "input": "合法边界、空输入、畸形片段",
          "mock": "隔离文件与网络",
          "assert": "合法通过；非法显式失败"
        }
      ]
    },
    {
      "semantic_unit_id": "exception:raise_for_status_exception_valueerror_semantic_tag_exception",
      "type": "exception",
      "source": "seed:dependency:raise_for_status; seed:variable:Exception; seed:variable:ValueError; semantic_tag→exception",
      "risk_score": 0.5075,
      "priority_score": 0.1984,
      "test_priority": "P0",
      "centrality_factor": 1.0,
      "call_chain": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion",
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient"
      ],
      "downstream": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "error_paths",
          "derived_from": "规则：type=exception → 覆盖错误分支与非法输入"
        },
        {
          "type": "exception_assertion",
          "derived_from": "规则：type=exception → 断言异常类型与信息"
        }
      ],
      "test_strategy": [
        {
          "scenario": "create_chat_completion：入参校验失败（内部异常路径）",
          "input": "None、空集合、违反不变量的结构体",
          "mock": "无需外网",
          "assert": "抛出 ValueError/TypeError 等与类型注解一致的异常"
        },
        {
          "scenario": "create_chat_completion：不变量破坏时的断言与错误消息",
          "input": "构造违反业务规则的中间状态",
          "mock": "必要时 patch 内部依赖返回非法组合",
          "assert": "异常信息包含可定位字段（字段名/错误码）"
        }
      ]
    },
    {
      "semantic_unit_id": "exception:raise_for_status_semantic_tag_exception",
      "type": "exception",
      "source": "seed:dependency:raise_for_status; semantic_tag→exception",
      "risk_score": 0.5075,
      "priority_score": 0.1984,
      "test_priority": "P0",
      "centrality_factor": 1.0,
      "call_chain": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "downstream": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "error_paths",
          "derived_from": "规则：type=exception → 覆盖错误分支与非法输入"
        },
        {
          "type": "exception_assertion",
          "derived_from": "规则：type=exception → 断言异常类型与信息"
        }
      ],
      "test_strategy": [
        {
          "scenario": "MyProviderClient：入参校验失败（内部异常路径）",
          "input": "None、空集合、违反不变量的结构体",
          "mock": "无需外网",
          "assert": "抛出 ValueError/TypeError 等与类型注解一致的异常"
        },
        {
          "scenario": "MyProviderClient：不变量破坏时的断言与错误消息",
          "input": "构造违反业务规则的中间状态",
          "mock": "必要时 patch 内部依赖返回非法组合",
          "assert": "异常信息包含可定位字段（字段名/错误码）"
        }
      ]
    },
    {
      "semantic_unit_id": "exception:semantic_tag_exception",
      "type": "exception",
      "source": "semantic_tag→exception",
      "risk_score": 0.5278,
      "priority_score": 0.1984,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "downstream": [],
      "integration_risk": true,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "error_paths",
          "derived_from": "规则：type=exception → 覆盖错误分支与非法输入"
        },
        {
          "type": "exception_assertion",
          "derived_from": "规则：type=exception → 断言异常类型与信息"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_config_for_model：入参校验失败（内部异常路径）",
          "input": "None、空集合、违反不变量的结构体",
          "mock": "无需外网",
          "assert": "抛出 ValueError/TypeError 等与类型注解一致的异常"
        },
        {
          "scenario": "get_config_for_model：不变量破坏时的断言与错误消息",
          "input": "构造违反业务规则的中间状态",
          "mock": "必要时 patch 内部依赖返回非法组合",
          "assert": "异常信息包含可定位字段（字段名/错误码）"
        }
      ]
    }
  ],
  "impact_graph": [
    {
      "file": "app/modules/intelligence/myprovider_client.py",
      "symbols": [
        {
          "name": "MyProviderClient",
          "entity_type": "class",
          "symbol_id": "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
          "semantic_unit_ids": [
            "api:stream_request_iter_lines_post_rstrip_time_semantic_tag_api",
            "config:getenv",
            "exception:raise_for_status_semantic_tag_exception"
          ],
          "centrality": 1.2
        },
        {
          "name": "create_chat_completion",
          "entity_type": "method",
          "symbol_id": "app/modules/intelligence/myprovider_client.py:method:create_chat_completion",
          "semantic_unit_ids": [
            "api:stream_request_post_time_semantic_tag_api",
            "config:getenv",
            "exception:raise_for_status_exception_valueerror_semantic_tag_exception"
          ],
          "centrality": 1.2
        }
      ]
    },
    {
      "file": "app/modules/intelligence/provider/llm_config.py",
      "symbols": [
        {
          "name": "get_config_for_model",
          "entity_type": "function",
          "symbol_id": "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
          "semantic_unit_ids": [
            "api:get_semantic_tag_api",
            "config:env_base_url_fallback_base_url",
            "data_processing:parse_model_string_any_model_config_map_fallback_auth_provider_model_string_os",
            "exception:semantic_tag_exception"
          ],
          "centrality": 1.2
        }
      ]
    },
    {
      "file": "app/modules/intelligence/provider/provider_service.py",
      "symbols": [
        {
          "name": "ProviderService",
          "entity_type": "class",
          "symbol_id": "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
          "semantic_unit_ids": [
            "api:build_config_for_model_identifier_build_llm_params_format_anthropic_multimodal_m",
            "config:get_api_key",
            "data_processing:validate_images_for_multimodal_semantic_tag_data_processing",
            "exception:semantic_tag_exception"
          ],
          "centrality": 1.2
        },
        {
          "name": "get_pydantic_model",
          "entity_type": "method",
          "symbol_id": "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
          "semantic_unit_ids": [
            "api:build_config_for_model_identifier_get_items_rstrip_warning_semantic_tag_api",
            "config:get_api_key",
            "data_processing:anthropicmodel_anthropicprovider_openaimodel_semantic_tag_data_processing"
          ],
          "centrality": 1.2
        }
      ]
    }
  ],
  "impact_test_plan": [
    {
      "target": "MyProviderClient",
      "symbol_id": "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
      "priority": "P0",
      "test_types": [
        "env",
        "exception",
        "integration",
        "mock"
      ],
      "estimated_cases": 7,
      "reason": "语义单元：api, config, exception；存在跨文件/多模块调用链（integration 风险）；最高测试优先级 P0（按 config/exception/api 优先规则）"
    },
    {
      "target": "create_chat_completion",
      "symbol_id": "app/modules/intelligence/myprovider_client.py:method:create_chat_completion",
      "priority": "P0",
      "test_types": [
        "env",
        "exception",
        "integration",
        "mock"
      ],
      "estimated_cases": 7,
      "reason": "语义单元：api, config, exception；最高测试优先级 P0（按 config/exception/api 优先规则）"
    },
    {
      "target": "get_config_for_model",
      "symbol_id": "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
      "priority": "P0",
      "test_types": [
        "env",
        "exception",
        "integration",
        "mock",
        "unit"
      ],
      "estimated_cases": 7,
      "reason": "语义单元：api, config, data_processing, exception；存在跨文件/多模块调用链（integration 风险）；最高测试优先级 P0（按 config/exception/api 优先规则）"
    },
    {
      "target": "ProviderService",
      "symbol_id": "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
      "priority": "P0",
      "test_types": [
        "env",
        "exception",
        "integration",
        "mock",
        "unit"
      ],
      "estimated_cases": 7,
      "reason": "语义单元：api, config, data_processing, exception；存在跨文件/多模块调用链（integration 风险）；最高测试优先级 P0（按 config/exception/api 优先规则）"
    },
    {
      "target": "get_pydantic_model",
      "symbol_id": "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
      "priority": "P0",
      "test_types": [
        "env",
        "integration",
        "mock",
        "unit"
      ],
      "estimated_cases": 5,
      "reason": "语义单元：api, config, data_processing；存在跨文件/多模块调用链（integration 风险）；最高测试优先级 P0（按 config/exception/api 优先规则）"
    }
  ],
  "impacted": [],
  "impacted_ranked": [],
  "debug": {
    "diff_stats": {
      "files": 6,
      "added": 104,
      "removed": 101
    },
    "change_graph": {
      "node_count": 73,
      "edge_count": 106
    },
    "code_change": {
      "files_analyzed": 6,
      "changes": 5,
      "used_llm": true,
      "llm_refine_files_invoked": 0,
      "llm_refine_files_skipped": 0,
      "cache_hits": 3,
      "cache_misses": 0,
      "cache_writes": 0,
      "elapsed_seconds": 0.014
    },
    "impact": {
      "mode": "impact_graph_v3",
      "candidate_count": 0,
      "ranked_count": 0,
      "used_llm": false,
      "change_graph_used": true,
      "propagation_hops_max": 3,
      "semantic_unit_catalog_count": 14,
      "impact_test_plan_count": 5,
      "top_priority_semantic_unit_ids": [
        "api:build_config_for_model_identifier_build_llm_params_format_anthropic_multimodal_m",
        "api:build_config_for_model_identifier_get_items_rstrip_warning_semantic_tag_api",
        "api:get_semantic_tag_api",
        "api:stream_request_iter_lines_post_rstrip_time_semantic_tag_api",
        "api:stream_request_post_time_semantic_tag_api",
        "config:env_base_url_fallback_base_url",
        "config:get_api_key",
        "config:getenv",
        "data_processing:anthropicmodel_anthropicprovider_openaimodel_semantic_tag_data_processing",
        "data_processing:parse_model_string_any_model_config_map_fallback_auth_provider_model_string_os",
        "data_processing:validate_images_for_multimodal_semantic_tag_data_processing",
        "exception:raise_for_status_exception_valueerror_semantic_tag_exception",
        "exception:raise_for_status_semantic_tag_exception",
        "exception:semantic_tag_exception"
      ],
      "impact_type_distribution": {
        "api": 5,
        "config": 3,
        "data_processing": 3,
        "exception": 3
      },
      "ranking_mode": "catalog_priority_minmax",
      "llm_error": null,
      "elapsed_seconds": 0.001,
      "llm_refine_enabled": false,
      "note": "主输出：semantic_units_catalog + impact_graph（symbol.semantic_unit_ids）+ impact_test_plan"
    }
  }
}

改进：
请在当前 ImpactAgent V3 基础上做增强（V4），重点解决“排序无效”和“语义粒度问题”。

---

# ❗改造1：修复 priority_score（必须拉开差距）

当前问题：
- 所有 priority_score 相同（无排序能力）

### 修改为：

priority_score =
  risk_score
× change_weight（changed file: 1.5, indirect: 1.0）
× centrality_factor（已有）
× log(1 + reference_count)
× integration_bonus（integration_risk ? 1.3 : 1.0）

要求：
- 输出必须呈现明显梯度（例如 0.2 ~ 0.9）
- debug 中输出排序 Top 5

---

# ❗改造2：拆分 semantic_unit（从“拼接”变“原子”）

当前问题：
- 一个 semantic_unit 包含多个行为（_build + _format + call_llm）

### 修改为：

一个 semantic_unit 只表示一个“原子能力”

例如拆分：

❌ 现在：
api:build_config_for_model_identifier_build_llm_params_format...

✅ 改成：
api:call_llm
api:format_multimodal_message
api:build_llm_params

要求：
- semantic_unit_id 简短、可复用
- 同类行为 across file 可复用

---

# ❗改造3：增强调用关系（补 upstream）

为 semantic_unit 增加：

"upstream": ["谁调用我"]
"edge_types": ["call", "config", "data"]

---

# ❗改造4：test_plan 动态化

当前问题：
- estimated_cases 基本固定

### 修改为：

estimated_cases =
  semantic_unit_count
× priority_score
× (integration_risk ? 1.5 : 1.0)

---

# ❗改造5：输出 Top Risk 集合（很重要）

新增：

"top_risks": [
  {
    "semantic_unit_id": "...",
    "reason": "高 priority_score + integration"
  }
]

---

# 输出要求

1️⃣ 更新后的 priority_score 示例（必须有差异）
2️⃣ semantic_unit 拆分后的示例
3️⃣ test_plan 变化对比
4️⃣ Top Risk 列表

{
  "repo_path": "/Users/admin/Desktop/potpie_bge",
  "changed_files": [
    ".env",
    ".env.template",
    "app/modules/intelligence/myprovider_client.py",
    "app/modules/intelligence/provider/llm_config.py",
    "app/modules/intelligence/provider/provider_service.py",
    "potpie-ui/.env"
  ],
  "semantic_units_catalog": [
    {
      "semantic_unit_id": "api:dependency_call",
      "type": "api",
      "source": "semantic_tag:dependency_call_changed",
      "risk_score": 0.4723,
      "priority_score": 0.9,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": true,
      "referenced_symbol_ids": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion",
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "MyProviderClient：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "MyProviderClient：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "exception:exception_handling",
      "type": "exception",
      "source": "semantic_tag:exception_handling_changed",
      "risk_score": 0.5278,
      "priority_score": 0.786738,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": true,
      "referenced_symbol_ids": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion",
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "error_paths",
          "derived_from": "规则：type=exception → 覆盖错误分支与非法输入"
        },
        {
          "type": "exception_assertion",
          "derived_from": "规则：type=exception → 断言异常类型与信息"
        }
      ],
      "test_strategy": [
        {
          "scenario": "MyProviderClient：入参校验失败（内部异常路径）",
          "input": "None、空集合、违反不变量的结构体",
          "mock": "无需外网",
          "assert": "抛出 ValueError/TypeError 等与类型注解一致的异常"
        },
        {
          "scenario": "MyProviderClient：不变量破坏时的断言与错误消息",
          "input": "构造违反业务规则的中间状态",
          "mock": "必要时 patch 内部依赖返回非法组合",
          "assert": "异常信息包含可定位字段（字段名/错误码）"
        }
      ]
    },
    {
      "semantic_unit_id": "api:rstrip",
      "type": "api",
      "source": "seed:dependency:rstrip",
      "risk_score": 0.4541,
      "priority_score": 0.679737,
      "test_priority": "P0",
      "centrality_factor": 1.0,
      "call_chain": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "downstream": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": true,
      "referenced_symbol_ids": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "MyProviderClient：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "MyProviderClient：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:get",
      "type": "api",
      "source": "seed:dependency:get",
      "risk_score": 0.4455,
      "priority_score": 0.668136,
      "test_priority": "P0",
      "centrality_factor": 1.0,
      "call_chain": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "downstream": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": true,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_config_for_model：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "get_config_for_model：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "config:get_api_key",
      "type": "config",
      "source": "seed:dependency:_get_api_key",
      "risk_score": 0.5093,
      "priority_score": 0.595035,
      "test_priority": "P0",
      "centrality_factor": 1.0,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "downstream": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "upstream": [],
      "edge_types": [
        "config"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "env_missing",
          "derived_from": "规则：type=config → 覆盖环境变量缺失"
        },
        {
          "type": "fallback",
          "derived_from": "规则：type=config → 覆盖默认值 / 配置回退"
        }
      ],
      "test_strategy": [
        {
          "scenario": "ProviderService：显式配置覆盖默认/回退（override 路径）",
          "input": "在同时提供默认值与显式参数/配置文件时调用",
          "mock": "patch 配置源顺序，制造后写覆盖先写",
          "assert": "显式配置优先生效；回退链路与文档一致"
        },
        {
          "scenario": "ProviderService：配置项类型或范围非法",
          "input": "注入非数字端口、空 URL、负数超时等",
          "mock": "patch 配置读取返回值",
          "assert": "拒绝非法配置并失败可测，不应静默继续"
        }
      ]
    },
    {
      "semantic_unit_id": "exception:raise_for_status",
      "type": "exception",
      "source": "seed:dependency:raise_for_status",
      "risk_score": 0.5075,
      "priority_score": 0.593234,
      "test_priority": "P0",
      "centrality_factor": 1.0,
      "call_chain": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "downstream": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "error_paths",
          "derived_from": "规则：type=exception → 覆盖错误分支与非法输入"
        },
        {
          "type": "exception_assertion",
          "derived_from": "规则：type=exception → 断言异常类型与信息"
        }
      ],
      "test_strategy": [
        {
          "scenario": "MyProviderClient：入参校验失败（内部异常路径）",
          "input": "None、空集合、违反不变量的结构体",
          "mock": "无需外网",
          "assert": "抛出 ValueError/TypeError 等与类型注解一致的异常"
        },
        {
          "scenario": "MyProviderClient：不变量破坏时的断言与错误消息",
          "input": "构造违反业务规则的中间状态",
          "mock": "必要时 patch 内部依赖返回非法组合",
          "assert": "异常信息包含可定位字段（字段名/错误码）"
        }
      ]
    },
    {
      "semantic_unit_id": "config:getenv",
      "type": "config",
      "source": "seed:dependency:getenv",
      "risk_score": 0.4897,
      "priority_score": 0.574533,
      "test_priority": "P0",
      "centrality_factor": 1.0,
      "call_chain": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "downstream": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "upstream": [],
      "edge_types": [
        "config"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "env_missing",
          "derived_from": "规则：type=config → 覆盖环境变量缺失"
        },
        {
          "type": "fallback",
          "derived_from": "规则：type=config → 覆盖默认值 / 配置回退"
        }
      ],
      "test_strategy": [
        {
          "scenario": "MyProviderClient：未设置关键环境变量时的行为（env 路径）",
          "input": "使用 monkeypatch.delenv 删除约定变量名后调用",
          "mock": "monkeypatch / patch.dict(os.environ, clear=True) 局部清除",
          "assert": "应抛出明确 ConfigurationError/ValueError 或使用文档记载的默认值"
        },
        {
          "scenario": "MyProviderClient：显式配置覆盖默认/回退（override 路径）",
          "input": "在同时提供默认值与显式参数/配置文件时调用",
          "mock": "patch 配置源顺序，制造后写覆盖先写",
          "assert": "显式配置优先生效；回退链路与文档一致"
        }
      ]
    },
    {
      "semantic_unit_id": "api:build_config_for_model_identifier",
      "type": "api",
      "source": "seed:dependency:_build_config_for_model_identifier",
      "risk_score": 0.4723,
      "priority_score": 0.556332,
      "test_priority": "P0",
      "centrality_factor": 1.0,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "downstream": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "ProviderService：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "ProviderService：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "data_processing:logic_branch",
      "type": "data_processing",
      "source": "semantic_tag:logic_branch_changed",
      "risk_score": 0.3519,
      "priority_score": 0.545431,
      "test_priority": "P1",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "call",
        "data"
      ],
      "integration_risk": true,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "boundary",
          "derived_from": "规则：type=data_processing → 边界值与空输入"
        },
        {
          "type": "invalid_input",
          "derived_from": "规则：type=data_processing → 非法格式/解析失败"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_config_for_model 数据解析/校验（app/modules/intelligence/provider/llm_config.py::get_config_for_model）",
          "input": "合法边界、空输入、畸形片段",
          "mock": "隔离文件与网络",
          "assert": "合法通过；非法显式失败"
        }
      ]
    },
    {
      "semantic_unit_id": "api:post",
      "type": "api",
      "source": "seed:dependency:post",
      "risk_score": 0.4541,
      "priority_score": 0.53733,
      "test_priority": "P0",
      "centrality_factor": 1.0,
      "call_chain": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "downstream": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "MyProviderClient：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "MyProviderClient：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:stream_request",
      "type": "api",
      "source": "seed:dependency:_stream_request",
      "risk_score": 0.4541,
      "priority_score": 0.537329,
      "test_priority": "P0",
      "centrality_factor": 1.0,
      "call_chain": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "downstream": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "MyProviderClient：流式响应中途取消/客户端断开",
          "input": "消费 generator/async iterator 若干 chunk 后关闭",
          "mock": "模拟 client 中断或 asyncio.CancelledError",
          "assert": "资源释放（连接/文件句柄）；无悬挂任务；错误可观测"
        },
        {
          "scenario": "MyProviderClient：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "MyProviderClient：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:time",
      "type": "api",
      "source": "seed:dependency:time",
      "risk_score": 0.4541,
      "priority_score": 0.537328,
      "test_priority": "P0",
      "centrality_factor": 1.0,
      "call_chain": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "downstream": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "MyProviderClient：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "MyProviderClient：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "exception:exception",
      "type": "exception",
      "source": "seed:variable:Exception",
      "risk_score": 0.5075,
      "priority_score": 0.330427,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "downstream": [],
      "upstream": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient"
      ],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "error_paths",
          "derived_from": "规则：type=exception → 覆盖错误分支与非法输入"
        },
        {
          "type": "exception_assertion",
          "derived_from": "规则：type=exception → 断言异常类型与信息"
        }
      ],
      "test_strategy": [
        {
          "scenario": "create_chat_completion：入参校验失败（内部异常路径）",
          "input": "None、空集合、违反不变量的结构体",
          "mock": "无需外网",
          "assert": "抛出 ValueError/TypeError 等与类型注解一致的异常"
        },
        {
          "scenario": "create_chat_completion：不变量破坏时的断言与错误消息",
          "input": "构造违反业务规则的中间状态",
          "mock": "必要时 patch 内部依赖返回非法组合",
          "assert": "异常信息包含可定位字段（字段名/错误码）"
        }
      ]
    },
    {
      "semantic_unit_id": "exception:value_error",
      "type": "exception",
      "source": "seed:variable:ValueError",
      "risk_score": 0.5075,
      "priority_score": 0.330426,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "downstream": [],
      "upstream": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient"
      ],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/myprovider_client.py:method:create_chat_completion"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "error_paths",
          "derived_from": "规则：type=exception → 覆盖错误分支与非法输入"
        },
        {
          "type": "exception_assertion",
          "derived_from": "规则：type=exception → 断言异常类型与信息"
        }
      ],
      "test_strategy": [
        {
          "scenario": "create_chat_completion：入参校验失败（内部异常路径）",
          "input": "None、空集合、违反不变量的结构体",
          "mock": "无需外网",
          "assert": "抛出 ValueError/TypeError 等与类型注解一致的异常"
        },
        {
          "scenario": "create_chat_completion：不变量破坏时的断言与错误消息",
          "input": "构造违反业务规则的中间状态",
          "mock": "必要时 patch 内部依赖返回非法组合",
          "assert": "异常信息包含可定位字段（字段名/错误码）"
        }
      ]
    },
    {
      "semantic_unit_id": "api:add",
      "type": "api",
      "source": "seed:dependency:add",
      "risk_score": 0.4723,
      "priority_score": 0.311825,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "ProviderService：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "ProviderService：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:append",
      "type": "api",
      "source": "seed:dependency:append",
      "risk_score": 0.4723,
      "priority_score": 0.311824,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "ProviderService：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "ProviderService：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:build_llm_params",
      "type": "api",
      "source": "seed:dependency:_build_llm_params",
      "risk_score": 0.4723,
      "priority_score": 0.311823,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "ProviderService：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "ProviderService：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:call_llm",
      "type": "api",
      "source": "seed:dependency:call_llm",
      "risk_score": 0.4723,
      "priority_score": 0.311822,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "ProviderService：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "ProviderService：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:format_anthropic_multimodal_message",
      "type": "api",
      "source": "seed:dependency:_format_anthropic_multimodal_message",
      "risk_score": 0.4723,
      "priority_score": 0.311821,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "ProviderService：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "ProviderService：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:format_gemini_multimodal_message",
      "type": "api",
      "source": "seed:dependency:_format_gemini_multimodal_message",
      "risk_score": 0.4723,
      "priority_score": 0.31182,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "ProviderService：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "ProviderService：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:format_multimodal_message",
      "type": "api",
      "source": "seed:dependency:_format_multimodal_message",
      "risk_score": 0.4723,
      "priority_score": 0.311819,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "ProviderService：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "ProviderService：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:format_multimodal_messages",
      "type": "api",
      "source": "seed:dependency:_format_multimodal_messages",
      "risk_score": 0.4723,
      "priority_score": 0.311818,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "ProviderService：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "ProviderService：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:format_openai_multimodal_message",
      "type": "api",
      "source": "seed:dependency:_format_openai_multimodal_message",
      "risk_score": 0.4723,
      "priority_score": 0.311817,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "ProviderService：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "ProviderService：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:validate_images_for_multimodal",
      "type": "api",
      "source": "seed:dependency:_validate_images_for_multimodal",
      "risk_score": 0.4723,
      "priority_score": 0.311816,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "ProviderService：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "ProviderService：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:iter_lines",
      "type": "api",
      "source": "seed:dependency:iter_lines",
      "risk_score": 0.4541,
      "priority_score": 0.302215,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "MyProviderClient：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "MyProviderClient：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:items",
      "type": "api",
      "source": "seed:dependency:items",
      "risk_score": 0.4455,
      "priority_score": 0.297714,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "downstream": [],
      "upstream": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_pydantic_model：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "get_pydantic_model：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "api:warning",
      "type": "api",
      "source": "seed:dependency:warning",
      "risk_score": 0.4455,
      "priority_score": 0.297713,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "downstream": [],
      "upstream": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "retry",
          "derived_from": "规则：type=api → 覆盖重试与退避"
        },
        {
          "type": "timeout",
          "derived_from": "规则：type=api → 覆盖超时行为"
        },
        {
          "type": "mock",
          "derived_from": "规则：type=api → 对外部 IO 使用 mock/stub"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_pydantic_model：依赖服务返回 5xx / 连接错误",
          "input": "可达 URL 但服务端错误",
          "mock": "MockTransport 返回 500",
          "assert": "重试策略或失败快速暴露；无无限阻塞"
        },
        {
          "scenario": "get_pydantic_model：请求超时",
          "input": "正常参数",
          "mock": "挂起响应直至 timeout",
          "assert": "在配置超时内失败并抛出可捕获超时异常"
        }
      ]
    },
    {
      "semantic_unit_id": "exception:input_validation",
      "type": "exception",
      "source": "semantic_tag:input_validation_added",
      "risk_score": 0.3906,
      "priority_score": 0.268712,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "call"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "error_paths",
          "derived_from": "规则：type=exception → 覆盖错误分支与非法输入"
        },
        {
          "type": "exception_assertion",
          "derived_from": "规则：type=exception → 断言异常类型与信息"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_config_for_model：入参校验失败（内部异常路径）",
          "input": "None、空集合、违反不变量的结构体",
          "mock": "无需外网",
          "assert": "抛出 ValueError/TypeError 等与类型注解一致的异常"
        },
        {
          "scenario": "get_config_for_model：不变量破坏时的断言与错误消息",
          "input": "构造违反业务规则的中间状态",
          "mock": "必要时 patch 内部依赖返回非法组合",
          "assert": "异常信息包含可定位字段（字段名/错误码）"
        }
      ]
    },
    {
      "semantic_unit_id": "config:env_base_url",
      "type": "config",
      "source": "seed:variable:env_base_url",
      "risk_score": 0.3769,
      "priority_score": 0.261511,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "config"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "env_missing",
          "derived_from": "规则：type=config → 覆盖环境变量缺失"
        },
        {
          "type": "fallback",
          "derived_from": "规则：type=config → 覆盖默认值 / 配置回退"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_config_for_model：显式配置覆盖默认/回退（override 路径）",
          "input": "在同时提供默认值与显式参数/配置文件时调用",
          "mock": "patch 配置源顺序，制造后写覆盖先写",
          "assert": "显式配置优先生效；回退链路与文档一致"
        },
        {
          "scenario": "get_config_for_model：配置项类型或范围非法",
          "input": "注入非数字端口、空 URL、负数超时等",
          "mock": "patch 配置读取返回值",
          "assert": "拒绝非法配置并失败可测，不应静默继续"
        }
      ]
    },
    {
      "semantic_unit_id": "config:fallback_base_url",
      "type": "config",
      "source": "seed:variable:fallback_base_url",
      "risk_score": 0.3769,
      "priority_score": 0.26151,
      "test_priority": "P0",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "config"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "env_missing",
          "derived_from": "规则：type=config → 覆盖环境变量缺失"
        },
        {
          "type": "fallback",
          "derived_from": "规则：type=config → 覆盖默认值 / 配置回退"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_config_for_model：显式配置覆盖默认/回退（override 路径）",
          "input": "在同时提供默认值与显式参数/配置文件时调用",
          "mock": "patch 配置源顺序，制造后写覆盖先写",
          "assert": "显式配置优先生效；回退链路与文档一致"
        },
        {
          "scenario": "get_config_for_model：配置项类型或范围非法",
          "input": "注入非数字端口、空 URL、负数超时等",
          "mock": "patch 配置读取返回值",
          "assert": "拒绝非法配置并失败可测，不应静默继续"
        }
      ]
    },
    {
      "semantic_unit_id": "data_processing:anthropic_model",
      "type": "data_processing",
      "source": "seed:function:AnthropicModel",
      "risk_score": 0.332,
      "priority_score": 0.237809,
      "test_priority": "P2",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "downstream": [],
      "upstream": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "edge_types": [
        "data"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "boundary",
          "derived_from": "规则：type=data_processing → 边界值与空输入"
        },
        {
          "type": "invalid_input",
          "derived_from": "规则：type=data_processing → 非法格式/解析失败"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_pydantic_model 数据解析/校验（app/modules/intelligence/provider/provider_service.py::get_pydantic_model）",
          "input": "合法边界、空输入、畸形片段",
          "mock": "隔离文件与网络",
          "assert": "合法通过；非法显式失败"
        }
      ]
    },
    {
      "semantic_unit_id": "data_processing:anthropic_provider",
      "type": "data_processing",
      "source": "seed:function:AnthropicProvider",
      "risk_score": 0.332,
      "priority_score": 0.237808,
      "test_priority": "P2",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "downstream": [],
      "upstream": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "edge_types": [
        "data"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "boundary",
          "derived_from": "规则：type=data_processing → 边界值与空输入"
        },
        {
          "type": "invalid_input",
          "derived_from": "规则：type=data_processing → 非法格式/解析失败"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_pydantic_model 数据解析/校验（app/modules/intelligence/provider/provider_service.py::get_pydantic_model）",
          "input": "合法边界、空输入、畸形片段",
          "mock": "隔离文件与网络",
          "assert": "合法通过；非法显式失败"
        }
      ]
    },
    {
      "semantic_unit_id": "data_processing:open_aimodel",
      "type": "data_processing",
      "source": "seed:function:OpenAIModel",
      "risk_score": 0.332,
      "priority_score": 0.237807,
      "test_priority": "P2",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "downstream": [],
      "upstream": [
        "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
        "app/modules/intelligence/provider/provider_service.py:class:ProviderService"
      ],
      "edge_types": [
        "data"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "boundary",
          "derived_from": "规则：type=data_processing → 边界值与空输入"
        },
        {
          "type": "invalid_input",
          "derived_from": "规则：type=data_processing → 非法格式/解析失败"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_pydantic_model 数据解析/校验（app/modules/intelligence/provider/provider_service.py::get_pydantic_model）",
          "input": "合法边界、空输入、畸形片段",
          "mock": "隔离文件与网络",
          "assert": "合法通过；非法显式失败"
        }
      ]
    },
    {
      "semantic_unit_id": "data_processing:any",
      "type": "data_processing",
      "source": "seed:variable:Any",
      "risk_score": 0.2604,
      "priority_score": 0.200006,
      "test_priority": "P2",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "data"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "boundary",
          "derived_from": "规则：type=data_processing → 边界值与空输入"
        },
        {
          "type": "invalid_input",
          "derived_from": "规则：type=data_processing → 非法格式/解析失败"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_config_for_model 数据解析/校验（app/modules/intelligence/provider/llm_config.py::get_config_for_model）",
          "input": "合法边界、空输入、畸形片段",
          "mock": "隔离文件与网络",
          "assert": "合法通过；非法显式失败"
        }
      ]
    },
    {
      "semantic_unit_id": "data_processing:fallback_auth_provider",
      "type": "data_processing",
      "source": "seed:variable:fallback_auth_provider",
      "risk_score": 0.2604,
      "priority_score": 0.200005,
      "test_priority": "P2",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "data"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "boundary",
          "derived_from": "规则：type=data_processing → 边界值与空输入"
        },
        {
          "type": "invalid_input",
          "derived_from": "规则：type=data_processing → 非法格式/解析失败"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_config_for_model 数据解析/校验（app/modules/intelligence/provider/llm_config.py::get_config_for_model）",
          "input": "合法边界、空输入、畸形片段",
          "mock": "隔离文件与网络",
          "assert": "合法通过；非法显式失败"
        }
      ]
    },
    {
      "semantic_unit_id": "data_processing:model_config_map",
      "type": "data_processing",
      "source": "seed:variable:MODEL_CONFIG_MAP",
      "risk_score": 0.2604,
      "priority_score": 0.200004,
      "test_priority": "P2",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "data"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "boundary",
          "derived_from": "规则：type=data_processing → 边界值与空输入"
        },
        {
          "type": "invalid_input",
          "derived_from": "规则：type=data_processing → 非法格式/解析失败"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_config_for_model 数据解析/校验（app/modules/intelligence/provider/llm_config.py::get_config_for_model）",
          "input": "合法边界、空输入、畸形片段",
          "mock": "隔离文件与网络",
          "assert": "合法通过；非法显式失败"
        }
      ]
    },
    {
      "semantic_unit_id": "data_processing:model_string",
      "type": "data_processing",
      "source": "seed:variable:model_string",
      "risk_score": 0.2604,
      "priority_score": 0.200003,
      "test_priority": "P2",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "data"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "boundary",
          "derived_from": "规则：type=data_processing → 边界值与空输入"
        },
        {
          "type": "invalid_input",
          "derived_from": "规则：type=data_processing → 非法格式/解析失败"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_config_for_model 数据解析/校验（app/modules/intelligence/provider/llm_config.py::get_config_for_model）",
          "input": "合法边界、空输入、畸形片段",
          "mock": "隔离文件与网络",
          "assert": "合法通过；非法显式失败"
        }
      ]
    },
    {
      "semantic_unit_id": "data_processing:os",
      "type": "data_processing",
      "source": "seed:variable:os",
      "risk_score": 0.2604,
      "priority_score": 0.200002,
      "test_priority": "P2",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "data"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "boundary",
          "derived_from": "规则：type=data_processing → 边界值与空输入"
        },
        {
          "type": "invalid_input",
          "derived_from": "规则：type=data_processing → 非法格式/解析失败"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_config_for_model 数据解析/校验（app/modules/intelligence/provider/llm_config.py::get_config_for_model）",
          "input": "合法边界、空输入、畸形片段",
          "mock": "隔离文件与网络",
          "assert": "合法通过；非法显式失败"
        }
      ]
    },
    {
      "semantic_unit_id": "data_processing:parse_model_string",
      "type": "data_processing",
      "source": "seed:function:parse_model_string; seed:variable:parse_model_string",
      "risk_score": 0.2604,
      "priority_score": 0.200001,
      "test_priority": "P2",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "data"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "boundary",
          "derived_from": "规则：type=data_processing → 边界值与空输入"
        },
        {
          "type": "invalid_input",
          "derived_from": "规则：type=data_processing → 非法格式/解析失败"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_config_for_model 数据解析/校验（app/modules/intelligence/provider/llm_config.py::get_config_for_model）",
          "input": "合法边界、空输入、畸形片段",
          "mock": "隔离文件与网络",
          "assert": "合法通过；非法显式失败"
        }
      ]
    },
    {
      "semantic_unit_id": "data_processing:provider",
      "type": "data_processing",
      "source": "seed:variable:provider",
      "risk_score": 0.2604,
      "priority_score": 0.2,
      "test_priority": "P2",
      "centrality_factor": 0.8,
      "call_chain": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "downstream": [],
      "upstream": [],
      "edge_types": [
        "data"
      ],
      "integration_risk": false,
      "referenced_symbol_ids": [
        "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model"
      ],
      "propagation_depth": 0,
      "test_focus": [
        {
          "type": "boundary",
          "derived_from": "规则：type=data_processing → 边界值与空输入"
        },
        {
          "type": "invalid_input",
          "derived_from": "规则：type=data_processing → 非法格式/解析失败"
        }
      ],
      "test_strategy": [
        {
          "scenario": "get_config_for_model 数据解析/校验（app/modules/intelligence/provider/llm_config.py::get_config_for_model）",
          "input": "合法边界、空输入、畸形片段",
          "mock": "隔离文件与网络",
          "assert": "合法通过；非法显式失败"
        }
      ]
    }
  ],
  "impact_graph": [
    {
      "file": "app/modules/intelligence/myprovider_client.py",
      "symbols": [
        {
          "name": "MyProviderClient",
          "entity_type": "class",
          "symbol_id": "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
          "semantic_unit_ids": [
            "api:dependency_call",
            "api:iter_lines",
            "api:post",
            "api:rstrip",
            "api:stream_request",
            "api:time",
            "config:getenv",
            "exception:exception_handling",
            "exception:raise_for_status"
          ],
          "centrality": 1.2
        },
        {
          "name": "create_chat_completion",
          "entity_type": "method",
          "symbol_id": "app/modules/intelligence/myprovider_client.py:method:create_chat_completion",
          "semantic_unit_ids": [
            "api:dependency_call",
            "api:post",
            "api:stream_request",
            "api:time",
            "config:getenv",
            "exception:exception",
            "exception:exception_handling",
            "exception:raise_for_status",
            "exception:value_error"
          ],
          "centrality": 1.2
        }
      ]
    },
    {
      "file": "app/modules/intelligence/provider/llm_config.py",
      "symbols": [
        {
          "name": "get_config_for_model",
          "entity_type": "function",
          "symbol_id": "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
          "semantic_unit_ids": [
            "api:dependency_call",
            "api:get",
            "config:env_base_url",
            "config:fallback_base_url",
            "data_processing:any",
            "data_processing:fallback_auth_provider",
            "data_processing:logic_branch",
            "data_processing:model_config_map",
            "data_processing:model_string",
            "data_processing:os",
            "data_processing:parse_model_string",
            "data_processing:provider",
            "exception:input_validation"
          ],
          "centrality": 1.2
        }
      ]
    },
    {
      "file": "app/modules/intelligence/provider/provider_service.py",
      "symbols": [
        {
          "name": "ProviderService",
          "entity_type": "class",
          "symbol_id": "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
          "semantic_unit_ids": [
            "api:add",
            "api:append",
            "api:build_config_for_model_identifier",
            "api:build_llm_params",
            "api:call_llm",
            "api:dependency_call",
            "api:format_anthropic_multimodal_message",
            "api:format_gemini_multimodal_message",
            "api:format_multimodal_message",
            "api:format_multimodal_messages",
            "api:format_openai_multimodal_message",
            "api:validate_images_for_multimodal",
            "config:get_api_key",
            "data_processing:logic_branch",
            "exception:exception_handling"
          ],
          "centrality": 1.2
        },
        {
          "name": "get_pydantic_model",
          "entity_type": "method",
          "symbol_id": "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
          "semantic_unit_ids": [
            "api:build_config_for_model_identifier",
            "api:dependency_call",
            "api:get",
            "api:items",
            "api:rstrip",
            "api:warning",
            "config:get_api_key",
            "data_processing:anthropic_model",
            "data_processing:anthropic_provider",
            "data_processing:logic_branch",
            "data_processing:open_aimodel"
          ],
          "centrality": 1.2
        }
      ]
    }
  ],
  "impact_test_plan": [
    {
      "target": "MyProviderClient",
      "symbol_id": "app/modules/intelligence/myprovider_client.py:class:MyProviderClient",
      "priority": "P0",
      "test_types": [
        "env",
        "exception",
        "integration",
        "mock"
      ],
      "estimated_cases": 8,
      "reason": "语义单元：api, config, exception；estimated_cases=9×avg_priority×1.5；存在跨文件/多模块调用链（integration 风险）；最高测试优先级 P0（按 config/exception/api 优先规则）"
    },
    {
      "target": "create_chat_completion",
      "symbol_id": "app/modules/intelligence/myprovider_client.py:method:create_chat_completion",
      "priority": "P0",
      "test_types": [
        "env",
        "exception",
        "integration",
        "mock"
      ],
      "estimated_cases": 8,
      "reason": "语义单元：api, config, exception；estimated_cases=9×avg_priority×1.5；存在跨文件/多模块调用链（integration 风险）；最高测试优先级 P0（按 config/exception/api 优先规则）"
    },
    {
      "target": "get_config_for_model",
      "symbol_id": "app/modules/intelligence/provider/llm_config.py:function:get_config_for_model",
      "priority": "P0",
      "test_types": [
        "env",
        "exception",
        "integration",
        "mock",
        "unit"
      ],
      "estimated_cases": 6,
      "reason": "语义单元：api, config, data_processing, exception；estimated_cases=13×avg_priority×1.5；存在跨文件/多模块调用链（integration 风险）；最高测试优先级 P0（按 config/exception/api 优先规则）"
    },
    {
      "target": "ProviderService",
      "symbol_id": "app/modules/intelligence/provider/provider_service.py:class:ProviderService",
      "priority": "P0",
      "test_types": [
        "env",
        "exception",
        "integration",
        "mock",
        "unit"
      ],
      "estimated_cases": 10,
      "reason": "语义单元：api, config, data_processing, exception；estimated_cases=15×avg_priority×1.5；存在跨文件/多模块调用链（integration 风险）；最高测试优先级 P0（按 config/exception/api 优先规则）"
    },
    {
      "target": "get_pydantic_model",
      "symbol_id": "app/modules/intelligence/provider/provider_service.py:method:get_pydantic_model",
      "priority": "P0",
      "test_types": [
        "env",
        "integration",
        "mock",
        "unit"
      ],
      "estimated_cases": 8,
      "reason": "语义单元：api, config, data_processing；estimated_cases=11×avg_priority×1.5；存在跨文件/多模块调用链（integration 风险）；最高测试优先级 P0（按 config/exception/api 优先规则）"
    }
  ],
  "top_risks": [
    {
      "semantic_unit_id": "api:dependency_call",
      "reason": "priority_score=0.900；integration 风险；多符号引用×5"
    },
    {
      "semantic_unit_id": "exception:exception_handling",
      "reason": "priority_score=0.787；integration 风险；多符号引用×3"
    },
    {
      "semantic_unit_id": "api:rstrip",
      "reason": "priority_score=0.680；integration 风险；多符号引用×2"
    },
    {
      "semantic_unit_id": "api:get",
      "reason": "priority_score=0.668；integration 风险；多符号引用×2"
    },
    {
      "semantic_unit_id": "config:get_api_key",
      "reason": "priority_score=0.595；多符号引用×2"
    },
    {
      "semantic_unit_id": "exception:raise_for_status",
      "reason": "priority_score=0.593；多符号引用×2"
    },
    {
      "semantic_unit_id": "config:getenv",
      "reason": "priority_score=0.575；多符号引用×2"
    },
    {
      "semantic_unit_id": "api:build_config_for_model_identifier",
      "reason": "priority_score=0.556；多符号引用×2"
    },
    {
      "semantic_unit_id": "data_processing:logic_branch",
      "reason": "priority_score=0.545；integration 风险；多符号引用×3"
    },
    {
      "semantic_unit_id": "api:post",
      "reason": "priority_score=0.537；多符号引用×2"
    },
    {
      "semantic_unit_id": "api:stream_request",
      "reason": "priority_score=0.537；多符号引用×2"
    },
    {
      "semantic_unit_id": "api:time",
      "reason": "priority_score=0.537；多符号引用×2"
    }
  ],
  "impacted": [],
  "impacted_ranked": [],
  "debug": {
    "diff_stats": {
      "files": 6,
      "added": 104,
      "removed": 101
    },
    "change_graph": {
      "node_count": 73,
      "edge_count": 106
    },
    "code_change": {
      "files_analyzed": 6,
      "changes": 5,
      "used_llm": true,
      "llm_refine_files_invoked": 0,
      "llm_refine_files_skipped": 0,
      "cache_hits": 3,
      "cache_misses": 0,
      "cache_writes": 0,
      "elapsed_seconds": 0.014
    },
    "impact": {
      "mode": "impact_graph_v4",
      "candidate_count": 0,
      "ranked_count": 0,
      "used_llm": false,
      "change_graph_used": true,
      "propagation_hops_max": 3,
      "semantic_unit_catalog_count": 40,
      "impact_test_plan_count": 5,
      "top_priority_semantic_unit_ids": [
        "api:dependency_call",
        "exception:exception_handling",
        "api:rstrip",
        "api:get",
        "config:get_api_key",
        "exception:raise_for_status",
        "config:getenv",
        "api:build_config_for_model_identifier",
        "data_processing:logic_branch",
        "api:post",
        "api:stream_request",
        "api:time",
        "exception:exception",
        "exception:value_error",
        "api:add"
      ],
      "priority_score_top_5": [
        {
          "semantic_unit_id": "api:dependency_call",
          "priority_score": 0.9,
          "reason": "score=0.9000; risk=0.472; integration"
        },
        {
          "semantic_unit_id": "exception:exception_handling",
          "priority_score": 0.786738,
          "reason": "score=0.7867; risk=0.528; integration"
        },
        {
          "semantic_unit_id": "api:rstrip",
          "priority_score": 0.679737,
          "reason": "score=0.6797; risk=0.454; integration"
        },
        {
          "semantic_unit_id": "api:get",
          "priority_score": 0.668136,
          "reason": "score=0.6681; risk=0.446; integration"
        },
        {
          "semantic_unit_id": "config:get_api_key",
          "priority_score": 0.595035,
          "reason": "score=0.5950; risk=0.509"
        }
      ],
      "impact_type_distribution": {
        "api": 20,
        "data_processing": 11,
        "exception": 5,
        "config": 4
      },
      "ranking_mode": "v4_risk_x_change_x_centrality_x_logrefs_x_integration_mapped_0.2_0.9",
      "llm_error": null,
      "elapsed_seconds": 0.002,
      "llm_refine_enabled": false,
      "note": "V4：semantic_units_catalog（原子 id）+ upstream/edge_types + impact_test_plan + top_risks"
    }
  }
}

