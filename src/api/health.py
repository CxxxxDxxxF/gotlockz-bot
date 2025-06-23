"""
Health Check API - FastAPI endpoints for monitoring
"""
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# Global bot reference
bot_instance = None

app = FastAPI(
    title="GotLockz Bot V2 API",
    description="Health check and monitoring endpoints",
    version="2.0.0"
)


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint."""
    return {
        "message": "GotLockz Bot V2 is running",
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for monitoring."""
    try:
        global bot_instance
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "bot_ready": False,
            "guild_count": 0,
            "latency": 0,
            "version": "2.0.0"
        }
        
        if bot_instance:
            health_data.update({
                "bot_ready": bot_instance.is_ready(),
                "guild_count": len(bot_instance.guilds),
                "latency": round(bot_instance.latency * 1000) if bot_instance.latency else 0
            })
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/status")
async def detailed_status() -> Dict[str, Any]:
    """Detailed status endpoint."""
    try:
        global bot_instance
        
        status_data = {
            "bot": {
                "status": "offline",
                "ready": False,
                "guilds": 0,
                "latency": 0,
                "uptime": 0
            },
            "system": {
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0"
            }
        }
        
        if bot_instance and bot_instance.is_ready():
            status_data["bot"].update({
                "status": "online",
                "ready": True,
                "guilds": len(bot_instance.guilds),
                "latency": round(bot_instance.latency * 1000) if bot_instance.latency else 0
            })
            
            # Calculate uptime if available
            if hasattr(bot_instance, 'start_time'):
                uptime = datetime.now() - bot_instance.start_time
                status_data["bot"]["uptime"] = uptime.total_seconds()
        
        return status_data
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")


@app.get("/guilds")
async def guild_info() -> Dict[str, Any]:
    """Get guild information."""
    try:
        global bot_instance
        
        if not bot_instance or not bot_instance.is_ready():
            raise HTTPException(status_code=503, detail="Bot not ready")
        
        guilds = []
        for guild in bot_instance.guilds:
            guilds.append({
                "id": guild.id,
                "name": guild.name,
                "member_count": guild.member_count,
                "owner_id": guild.owner_id
            })
        
        return {
            "guilds": guilds,
            "total_guilds": len(guilds),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Guild info error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get guild information")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"API error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


def set_bot_instance(bot):
    """Set the global bot instance for health checks."""
    global bot_instance
    bot_instance = bot
    logger.info("Bot instance set for health checks") 