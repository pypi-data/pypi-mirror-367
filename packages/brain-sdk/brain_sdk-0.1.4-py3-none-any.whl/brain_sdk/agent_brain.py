import asyncio
import os
import signal
import threading
import time
from datetime import datetime
from typing import Optional

import requests
from brain_sdk.types import AgentStatus, HeartbeatData
from brain_sdk.logger import log_heartbeat, log_track, log_debug, log_warn, log_error, log_success, log_setup, log_info


class AgentBrain:
    """
    Brain Server Communication handler for Agent class.
    
    This class encapsulates all Brain server communication functionality including:
    - Agent registration with Brain server
    - Heartbeat management (both simple and enhanced)
    - Fast lifecycle management
    - Graceful shutdown notifications
    - Signal handling for fast shutdown
    """

    def __init__(self, agent_instance):
        """
        Initialize the Brain handler with a reference to the agent instance.
        
        Args:
            agent_instance: The Agent instance this handler belongs to
        """
        self.agent = agent_instance

    async def register_with_brain_server(self, port: int):
        """Register this agent node with Brain server"""
        self.agent.base_url = f"http://localhost:{port}"

        try:
            log_debug(f"Attempting to register with Brain server at {self.agent.brain_server}")
            success = await self.agent.client.register_agent(
                node_id=self.agent.node_id,
                reasoners=self.agent.reasoners,
                skills=self.agent.skills,
                base_url=self.agent.base_url,
            )
            if success:
                log_success(f"Registered node '{self.agent.node_id}' with Brain server")
                self.agent.brain_connected = True
                
                # Attempt DID registration after successful Brain registration
                if self.agent.did_manager:
                    did_success = self.agent._register_agent_with_did()
                    if not did_success and self.agent.dev_mode:
                        log_warn("DID registration failed, continuing without DID functionality")
            else:
                log_error("Registration failed")
                self.agent.brain_connected = False

        except Exception as e:
            self.agent.brain_connected = False
            if self.agent.dev_mode:
                log_warn(f"Brain server not available: {e}")
                log_setup("Running in development mode - agent will work standalone")
                log_info(f"To connect to Brain server, start it at {self.agent.brain_server}")
            else:
                log_error(f"Failed to register with Brain server: {e}")
                if (
                    isinstance(e, requests.exceptions.RequestException)
                    and e.response is not None
                ):
                    log_warn(f"Response status: {e.response.status_code}")
                    log_warn(f"Response text: {e.response.text}")
                raise

    def send_heartbeat(self):
        """Send heartbeat to Brain server"""
        if not self.agent.brain_connected:
            return  # Skip heartbeat if not connected to Brain

        try:
            response = requests.post(
                f"{self.agent.brain_server}/api/v1/nodes/{self.agent.node_id}/heartbeat",
                headers={"Content-Type": "application/json"},
                timeout=5,
            )
            if response.status_code == 200:
                log_heartbeat("Heartbeat sent successfully")
            else:
                log_warn(f"Heartbeat failed with status {response.status_code}: {response.text}")
        except Exception as e:
            log_error(f"Failed to send heartbeat: {e}")

    def heartbeat_worker(self, interval: int = 30):
        """Background worker that sends periodic heartbeats"""
        if not self.agent.brain_connected:
            log_heartbeat("Heartbeat worker skipped - not connected to Brain server")
            return

        log_heartbeat(f"Starting heartbeat worker (interval: {interval}s)")
        while not self.agent._heartbeat_stop_event.wait(interval):
            self.send_heartbeat()
        log_heartbeat("Heartbeat worker stopped")

    def start_heartbeat(self, interval: int = 30):
        """Start the heartbeat background thread"""
        if not self.agent.brain_connected:
            return  # Skip heartbeat if not connected to Brain

        if self.agent._heartbeat_thread is None or not self.agent._heartbeat_thread.is_alive():
            self.agent._heartbeat_stop_event.clear()
            self.agent._heartbeat_thread = threading.Thread(
                target=self.heartbeat_worker, args=(interval,), daemon=True
            )
            self.agent._heartbeat_thread.start()

    def stop_heartbeat(self):
        """Stop the heartbeat background thread"""
        if self.agent._heartbeat_thread and self.agent._heartbeat_thread.is_alive():
            print("💓 Stopping heartbeat worker...")
            self.agent._heartbeat_stop_event.set()
            self.agent._heartbeat_thread.join(timeout=5)

    async def send_enhanced_heartbeat(self) -> bool:
        """
        Send enhanced heartbeat with current status and MCP information.

        Returns:
            True if heartbeat was successful, False otherwise
        """
        if not self.agent.brain_connected:
            return False

        try:
            # Get MCP server health information
            mcp_servers = self.agent.mcp_handler._get_mcp_server_health()

            # Create heartbeat data
            heartbeat_data = HeartbeatData(
                status=self.agent._current_status,
                mcp_servers=mcp_servers,
                timestamp=datetime.now().isoformat(),
            )

            # Send enhanced heartbeat
            success = await self.agent.client.send_enhanced_heartbeat(
                self.agent.node_id, heartbeat_data
            )

            if success:
                log_heartbeat(f"Enhanced heartbeat sent - Status: {self.agent._current_status.value}")

            return success

        except Exception as e:
            if self.agent.dev_mode:
                print(f"❌ Enhanced heartbeat failed: {e}")
            return False

    async def notify_shutdown(self) -> bool:
        """
        Notify Brain server of graceful shutdown.

        Returns:
            True if notification was successful, False otherwise
        """
        if not self.agent.brain_connected:
            return False

        try:
            success = await self.agent.client.notify_graceful_shutdown(self.agent.node_id)
            if self.agent.dev_mode and success:
                print("🛑 Graceful shutdown notification sent")
            return success
        except Exception as e:
            if self.agent.dev_mode:
                print(f"⚠️ Shutdown notification failed: {e}")
            return False

    def setup_fast_lifecycle_signal_handlers(self) -> None:
        """
        Setup signal handlers for fast lifecycle management.
        """

        def signal_handler(signum: int, frame) -> None:
            """Handle shutdown signals with immediate notification"""
            signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"

            if self.agent.dev_mode:
                print(f"\n🛑 {signal_name} received - fast shutdown initiated")

            # Set shutdown flag
            self.agent._shutdown_requested = True
            self.agent._current_status = AgentStatus.OFFLINE

            # Try to notify Brain server immediately (synchronous)
            try:
                success = self.agent.client.notify_graceful_shutdown_sync(self.agent.node_id)
                if self.agent.dev_mode:
                    print(
                        f"🛑 Shutdown notification: {'✅ sent' if success else '❌ failed'}"
                    )
            except Exception as e:
                if self.agent.dev_mode:
                    print(f"⚠️ Shutdown notification error: {e}")

            # Cleanup and exit
            self.agent.mcp_handler._cleanup_mcp_servers()
            # Clear agent from thread-local storage before exit
            from brain_sdk.agent_registry import clear_current_agent
            clear_current_agent()
            os._exit(0)

        try:
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)

            if self.agent.dev_mode:
                print("🔧 Fast lifecycle signal handlers registered")

        except Exception as e:
            if self.agent.dev_mode:
                print(f"⚠️ Failed to setup signal handlers: {e}")

    async def register_with_fast_lifecycle(self, port: int) -> bool:
        """
        Register agent with immediate status reporting for fast lifecycle.

        Args:
            port: The port the agent is running on

        Returns:
            True if registration was successful, False otherwise
        """
        self.agent.base_url = f"http://localhost:{port}"

        try:
            if self.agent.dev_mode:
                print(f"🔗 Fast registration with Brain server at {self.agent.brain_server}")

            # Register with STARTING status for immediate visibility
            success = await self.agent.client.register_agent_with_status(
                node_id=self.agent.node_id,
                reasoners=self.agent.reasoners,
                skills=self.agent.skills,
                base_url=self.agent.base_url,
                status=AgentStatus.STARTING,
            )

            if success:
                if self.agent.dev_mode:
                    print(
                        f"✅ Fast registration successful - Status: {AgentStatus.STARTING.value}"
                    )
                self.agent.brain_connected = True
                
                # Attempt DID registration after successful Brain registration
                if self.agent.did_manager:
                    did_success = self.agent._register_agent_with_did()
                    if not did_success and self.agent.dev_mode:
                        print("⚠️ DID registration failed, continuing without DID functionality")
                
                return True
            else:
                if self.agent.dev_mode:
                    print("❌ Fast registration failed")
                self.agent.brain_connected = False
                return False

        except Exception as e:
            self.agent.brain_connected = False
            if self.agent.dev_mode:
                print(f"⚠️ Fast registration error: {e}")
            return False

    async def enhanced_heartbeat_loop(self, interval: int) -> None:
        """
        Background loop for sending enhanced heartbeats with status and MCP information.

        Args:
            interval: Heartbeat interval in seconds
        """
        if self.agent.dev_mode:
            print(f"💓 Enhanced heartbeat loop started (interval: {interval}s)")

        while not self.agent._shutdown_requested:
            try:
                # Send enhanced heartbeat
                success = await self.send_enhanced_heartbeat()

                if not success and self.agent.dev_mode:
                    print("⚠️ Enhanced heartbeat failed - retrying next cycle")

                # Wait for next heartbeat interval
                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                if self.agent.dev_mode:
                    print("💓 Enhanced heartbeat loop cancelled")
                break
            except Exception as e:
                if self.agent.dev_mode:
                    print(f"⚠️ Enhanced heartbeat loop error: {e}")
                # Continue loop even on errors
                await asyncio.sleep(interval)

        if self.agent.dev_mode:
            print("💓 Enhanced heartbeat loop stopped")
