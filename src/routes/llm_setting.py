from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR
from logs import log_info, log_error
from schemes import LLMsSettings, llm_config
from llm import HuggingFaceLLM

llm_setting_route = APIRouter()

@llm_setting_route.post("/llmConfiguration")
async def llm_setting(body: LLMsSettings, request: Request) -> JSONResponse:
    """Endpoint to update LLM configuration"""
    try:
        # Update configuration
        config_updates = {
            "model_name": body.model_name,
            "max_new_tokens": body.max_new_tokens,
            "do_sample": body.do_sample,
            "temperature": body.temperature,
            "top_p": body.top_p,
            "top_k": body.top_k,
            "trust_remote_code": body.trust_remote_code,
            "quantization": body.quantization,
            "quantization_type": body.quantization_type
        }
        llm_config.update(config_updates)
        
        # Reinitialize LLM with new config
        request.app.state.llm = HuggingFaceLLM(**llm_config)
        log_info(f"LLM reconfigured with: {config_updates}")

        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "status": "success",
                "message": "LLM configuration updated successfully",
                "config": llm_config
            }
        )
    except Exception as e:
        log_error(f"LLM configuration failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": f"Failed to configure LLM: {str(e)}"
            }
        )