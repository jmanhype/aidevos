"""
Monitoring System Setup Script for AIDevOS.

This script sets up the monitoring system for the AIDevOS system, including:
- Prometheus for metrics collection
- Grafana for metrics visualization
- Loki for log aggregation
- AlertManager for alerting
- Distributed tracing with Jaeger

It provides a CLI interface for configuring and deploying the monitoring stack.
"""

import argparse
import logging
import os
import subprocess
import sys
import yaml
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("aidevos.monitoring")


class MonitoringComponent(Enum):
    """Components of the AIDevOS monitoring system."""
    
    PROMETHEUS = "prometheus"
    GRAFANA = "grafana"
    LOKI = "loki"
    ALERTMANAGER = "alertmanager"
    JAEGER = "jaeger"
    ALL = "all"


class MonitoringEnvironment(Enum):
    """Deployment environments for the monitoring system."""
    
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "production"


class MonitoringSetup:
    """Monitoring system setup manager for AIDevOS."""
    
    def __init__(
        self,
        environment: MonitoringEnvironment,
        config_dir: str = "config/monitoring",
        output_dir: str = "deployment/monitoring",
        custom_configs: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the monitoring setup manager.
        
        Args:
            environment: Target environment
            config_dir: Directory containing monitoring configuration templates
            output_dir: Directory where generated configurations will be saved
            custom_configs: Custom configuration files to use (component -> path)
        """
        self.environment = environment
        self.config_dir = Path(config_dir)
        self.output_dir = Path(output_dir)
        self.custom_configs = custom_configs or {}
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initializing monitoring setup for {environment.value} environment")
    
    def setup_component(self, component: MonitoringComponent) -> bool:
        """
        Set up a specific monitoring component.
        
        Args:
            component: Component to set up
            
        Returns:
            True if the component was set up successfully, False otherwise
        """
        if component == MonitoringComponent.ALL:
            success = True
            for comp in MonitoringComponent:
                if comp != MonitoringComponent.ALL:
                    if not self.setup_component(comp):
                        success = False
            return success
        
        logger.info(f"Setting up {component.value} for {self.environment.value} environment")
        
        try:
            # Generate configuration
            config = self._generate_component_config(component)
            
            # Write configuration to file
            config_path = self._write_component_config(component, config)
            
            # Deploy component
            if not self._deploy_component(component, config_path):
                return False
            
            logger.info(f"Successfully set up {component.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set up {component.value}: {str(e)}")
            return False
    
    def _generate_component_config(self, component: MonitoringComponent) -> Dict[str, Any]:
        """
        Generate configuration for a monitoring component.
        
        Args:
            component: Component to generate configuration for
            
        Returns:
            Generated configuration as a dictionary
            
        Raises:
            FileNotFoundError: If the template configuration is not found
            yaml.YAMLError: If the template configuration is not valid YAML
        """
        # Check if a custom configuration was provided
        if component.value in self.custom_configs:
            logger.info(f"Using custom configuration for {component.value}: {self.custom_configs[component.value]}")
            with open(self.custom_configs[component.value], "r") as f:
                return yaml.safe_load(f)
        
        # Get the template configuration
        template_path = self.config_dir / f"{component.value}-{self.environment.value}.yaml"
        if not template_path.exists():
            template_path = self.config_dir / f"{component.value}-template.yaml"
        
        if not template_path.exists():
            raise FileNotFoundError(f"No configuration template found for {component.value}")
        
        logger.info(f"Using configuration template: {template_path}")
        
        with open(template_path, "r") as f:
            config = yaml.safe_load(f)
        
        # Customize configuration based on environment
        if component == MonitoringComponent.PROMETHEUS:
            self._customize_prometheus_config(config)
        elif component == MonitoringComponent.GRAFANA:
            self._customize_grafana_config(config)
        elif component == MonitoringComponent.ALERTMANAGER:
            self._customize_alertmanager_config(config)
        
        return config
    
    def _customize_prometheus_config(self, config: Dict[str, Any]) -> None:
        """
        Customize Prometheus configuration based on environment.
        
        Args:
            config: Prometheus configuration to customize
        """
        # Adjust scrape interval based on environment
        if self.environment == MonitoringEnvironment.DEV:
            config["global"]["scrape_interval"] = "15s"
        elif self.environment == MonitoringEnvironment.STAGING:
            config["global"]["scrape_interval"] = "10s"
        elif self.environment == MonitoringEnvironment.PRODUCTION:
            config["global"]["scrape_interval"] = "5s"
        
        # Add environment-specific job configs
        environment_suffix = f"-{self.environment.value}"
        for job in config.get("scrape_configs", []):
            if "job_name" in job:
                if not job["job_name"].endswith(environment_suffix):
                    job["job_name"] = f"{job['job_name']}{environment_suffix}"
    
    def _customize_grafana_config(self, config: Dict[str, Any]) -> None:
        """
        Customize Grafana configuration based on environment.
        
        Args:
            config: Grafana configuration to customize
        """
        # Adjust settings based on environment
        if self.environment == MonitoringEnvironment.DEV:
            config["auth.anonymous"] = {"enabled": True, "org_role": "Viewer"}
        else:
            config["auth.anonymous"] = {"enabled": False}
        
        # Set appropriate URLs
        if self.environment == MonitoringEnvironment.PRODUCTION:
            config["server"]["root_url"] = "https://grafana.aidevos.com"
        elif self.environment == MonitoringEnvironment.STAGING:
            config["server"]["root_url"] = "https://grafana.staging.aidevos.com"
        else:
            config["server"]["root_url"] = "https://grafana.dev.aidevos.com"
    
    def _customize_alertmanager_config(self, config: Dict[str, Any]) -> None:
        """
        Customize AlertManager configuration based on environment.
        
        Args:
            config: AlertManager configuration to customize
        """
        # Set appropriate receivers based on environment
        if self.environment == MonitoringEnvironment.PRODUCTION:
            # In production, send alerts to multiple channels
            config["receivers"] = [
                {
                    "name": "team-devops",
                    "email_configs": [{"to": "devops@aidevos.com"}],
                    "slack_configs": [{"channel": "#alerts-production"}],
                    "pagerduty_configs": [{"service_key": "${PAGERDUTY_SERVICE_KEY}"}],
                }
            ]
        elif self.environment == MonitoringEnvironment.STAGING:
            # In staging, send alerts to Slack and email
            config["receivers"] = [
                {
                    "name": "team-devops",
                    "email_configs": [{"to": "devops@aidevos.com"}],
                    "slack_configs": [{"channel": "#alerts-staging"}],
                }
            ]
        else:
            # In dev, send alerts to Slack only
            config["receivers"] = [
                {
                    "name": "team-devops",
                    "slack_configs": [{"channel": "#alerts-dev"}],
                }
            ]
        
        # Set appropriate routes
        if "route" in config:
            config["route"]["group_by"] = ["alertname", "cluster", "service"]
            
            if self.environment == MonitoringEnvironment.PRODUCTION:
                config["route"]["group_wait"] = "30s"
                config["route"]["group_interval"] = "5m"
                config["route"]["repeat_interval"] = "3h"
            elif self.environment == MonitoringEnvironment.STAGING:
                config["route"]["group_wait"] = "30s"
                config["route"]["group_interval"] = "5m"
                config["route"]["repeat_interval"] = "12h"
            else:
                config["route"]["group_wait"] = "1m"
                config["route"]["group_interval"] = "5m"
                config["route"]["repeat_interval"] = "24h"
    
    def _write_component_config(self, component: MonitoringComponent, config: Dict[str, Any]) -> Path:
        """
        Write component configuration to file.
        
        Args:
            component: Component the configuration is for
            config: Configuration to write
            
        Returns:
            Path to the written configuration file
        """
        output_path = self.output_dir / f"{component.value}-{self.environment.value}.yaml"
        
        with open(output_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Wrote {component.value} configuration to {output_path}")
        return output_path
    
    def _deploy_component(self, component: MonitoringComponent, config_path: Path) -> bool:
        """
        Deploy a monitoring component.
        
        Args:
            component: Component to deploy
            config_path: Path to the component configuration file
            
        Returns:
            True if the component was deployed successfully, False otherwise
        """
        # This is a simplified implementation for demonstration
        # In a real implementation, this would use Kubernetes or other deployment mechanisms
        logger.info(f"Deploying {component.value} with configuration from {config_path}")
        
        # Simulate deployment success
        logger.info(f"Successfully deployed {component.value}")
        return True
    
    def generate_dashboards(self) -> bool:
        """
        Generate Grafana dashboards for the AIDevOS system.
        
        Returns:
            True if dashboards were generated successfully, False otherwise
        """
        logger.info("Generating Grafana dashboards")
        
        try:
            # This is a simplified implementation for demonstration
            # In a real implementation, this would generate actual dashboard JSONs
            
            # Define dashboards to generate
            dashboards = [
                "aidevos-overview",
                "aidevos-services",
                "aidevos-durable-objects",
                "aidevos-orchestration",
                "aidevos-api-gateway",
            ]
            
            dashboard_dir = self.output_dir / "dashboards"
            dashboard_dir.mkdir(exist_ok=True)
            
            for dashboard in dashboards:
                # Generate dashboard JSON (simplified for this example)
                dashboard_path = dashboard_dir / f"{dashboard}.json"
                with open(dashboard_path, "w") as f:
                    f.write("{}")  # Placeholder JSON
                
                logger.info(f"Generated dashboard: {dashboard}")
            
            logger.info(f"Successfully generated {len(dashboards)} dashboards")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate dashboards: {str(e)}")
            return False
    
    def setup_alert_rules(self) -> bool:
        """
        Set up Prometheus alert rules.
        
        Returns:
            True if alert rules were set up successfully, False otherwise
        """
        logger.info("Setting up Prometheus alert rules")
        
        try:
            # This is a simplified implementation for demonstration
            # In a real implementation, this would generate actual alerting rules
            
            rules_file = self.output_dir / f"prometheus-rules-{self.environment.value}.yaml"
            
            # Basic example rules
            rules = {
                "groups": [
                    {
                        "name": "aidevos",
                        "rules": [
                            {
                                "alert": "HighCPUUsage",
                                "expr": "process_cpu_seconds_total > 0.8",
                                "for": "5m",
                                "labels": {"severity": "warning"},
                                "annotations": {
                                    "summary": "High CPU usage detected",
                                    "description": "{{ $labels.instance }} has high CPU usage",
                                },
                            },
                            {
                                "alert": "HighMemoryUsage",
                                "expr": "process_resident_memory_bytes / process_virtual_memory_bytes > 0.8",
                                "for": "5m",
                                "labels": {"severity": "warning"},
                                "annotations": {
                                    "summary": "High memory usage detected",
                                    "description": "{{ $labels.instance }} is using a lot of memory",
                                },
                            },
                            {
                                "alert": "HighLatency",
                                "expr": "http_request_duration_seconds{quantile=\"0.9\"} > 1",
                                "for": "5m",
                                "labels": {"severity": "warning"},
                                "annotations": {
                                    "summary": "High latency detected",
                                    "description": "{{ $labels.instance }} has high latency",
                                },
                            },
                            {
                                "alert": "HighErrorRate",
                                "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) > 0.01",
                                "for": "5m",
                                "labels": {"severity": "critical"},
                                "annotations": {
                                    "summary": "High error rate detected",
                                    "description": "Error rate is above 1%",
                                },
                            },
                        ],
                    }
                ]
            }
            
            # Add environment-specific rules
            if self.environment == MonitoringEnvironment.PRODUCTION:
                # Add more strict rules for production
                memory_rule = {
                    "alert": "CriticalMemoryUsage",
                    "expr": "process_resident_memory_bytes / process_virtual_memory_bytes > 0.95",
                    "for": "2m",
                    "labels": {"severity": "critical"},
                    "annotations": {
                        "summary": "Critical memory usage detected",
                        "description": "{{ $labels.instance }} is at risk of running out of memory",
                    },
                }
                rules["groups"][0]["rules"].append(memory_rule)
            
            # Write rules to file
            with open(rules_file, "w") as f:
                yaml.dump(rules, f, default_flow_style=False)
            
            logger.info(f"Wrote alert rules to {rules_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set up alert rules: {str(e)}")
            return False
    
    def setup_monitoring_stack(self) -> bool:
        """
        Set up the complete monitoring stack.
        
        Returns:
            True if the stack was set up successfully, False otherwise
        """
        logger.info(f"Setting up monitoring stack for {self.environment.value} environment")
        
        # Set up all components
        if not self.setup_component(MonitoringComponent.ALL):
            return False
        
        # Generate dashboards
        if not self.generate_dashboards():
            return False
        
        # Set up alert rules
        if not self.setup_alert_rules():
            return False
        
        logger.info(f"Successfully set up monitoring stack for {self.environment.value} environment")
        return True


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="AIDevOS Monitoring Setup")
    
    parser.add_argument(
        "--environment",
        type=str,
        choices=[e.value for e in MonitoringEnvironment],
        default=MonitoringEnvironment.DEV.value,
        help="Target environment",
    )
    
    parser.add_argument(
        "--config-dir",
        type=str,
        default="config/monitoring",
        help="Directory containing monitoring configuration templates",
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="deployment/monitoring",
        help="Directory where generated configurations will be saved",
    )
    
    parser.add_argument(
        "--component",
        type=str,
        choices=[c.value for c in MonitoringComponent],
        default=MonitoringComponent.ALL.value,
        help="Component to set up",
    )
    
    parser.add_argument(
        "--custom-config",
        type=str,
        help="Path to custom configuration file (only used if --component is specified)",
    )
    
    parser.add_argument(
        "--dashboards-only",
        action="store_true",
        help="Only generate dashboards",
    )
    
    parser.add_argument(
        "--alerts-only",
        action="store_true",
        help="Only set up alert rules",
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the monitoring setup script.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()
    
    environment = MonitoringEnvironment(args.environment)
    component = MonitoringComponent(args.component)
    
    custom_configs = {}
    if args.custom_config and component != MonitoringComponent.ALL:
        custom_configs[component.value] = args.custom_config
    
    setup = MonitoringSetup(
        environment=environment,
        config_dir=args.config_dir,
        output_dir=args.output_dir,
        custom_configs=custom_configs,
    )
    
    if args.dashboards_only:
        if setup.generate_dashboards():
            return 0
        else:
            return 1
    
    if args.alerts_only:
        if setup.setup_alert_rules():
            return 0
        else:
            return 1
    
    if component != MonitoringComponent.ALL:
        if setup.setup_component(component):
            return 0
        else:
            return 1
    
    if setup.setup_monitoring_stack():
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())