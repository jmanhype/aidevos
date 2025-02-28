#!/usr/bin/env python3
"""
DSPy modules for AI agents.

This module provides DSPy-based implementations for AI team agents,
allowing them to use language models for their reasoning and responses.
"""

import dspy
import json
import logging
from typing import Dict, List, Any, Optional

# Set up logging
logger = logging.getLogger("aidevos.dspy_modules")
logger.setLevel(logging.INFO)

# Initialize the DSPy language model
LM = dspy.LM(model="gpt-4")
dspy.settings.configure(lm=LM)


class AgentSignature(dspy.Signature):
    """Base signature for all agents."""
    
    agent_id = dspy.InputField(desc="Unique identifier for the agent")
    agent_role = dspy.InputField(desc="Role of the agent (PM, Dev, DevOps, UX)")
    task = dspy.InputField(desc="The task to process")
    context = dspy.InputField(desc="Additional context information")
    response = dspy.OutputField(desc="The agent's response to the task")


class RequirementsAnalyzerSignature(dspy.Signature):
    """Signature for requirements analysis."""
    project_description = dspy.InputField()
    requirements = dspy.OutputField(desc="Comprehensive requirements analysis")


class ArchitectureDesignerSignature(dspy.Signature):
    """Signature for architecture design."""
    requirements = dspy.InputField()
    architecture = dspy.OutputField(desc="System architecture design")


class ArchitectureFinalizerSignature(dspy.Signature):
    """Signature for architecture finalization."""
    initial_architecture = dspy.InputField()
    feedback = dspy.InputField()
    final_architecture = dspy.OutputField(desc="Finalized architecture incorporating feedback")


class FeaturePlannerSignature(dspy.Signature):
    """Signature for feature planning."""
    architecture = dspy.InputField()
    requirements = dspy.InputField()
    feature_plan = dspy.OutputField(desc="Detailed feature roadmap")


class CodeImplementerSignature(dspy.Signature):
    """Signature for code implementation."""
    service_name = dspy.InputField()
    requirements = dspy.InputField()
    architecture = dspy.InputField()
    code = dspy.OutputField(desc="Implementation code")


class CodeReviewerSignature(dspy.Signature):
    """Signature for code review."""
    code = dspy.InputField()
    review = dspy.OutputField(desc="Code review feedback")


class ArchitectureReviewerSignature(dspy.Signature):
    """Signature for architecture review."""
    architecture = dspy.InputField()
    review = dspy.OutputField(desc="Architecture review feedback")


class ImplementationPlannerSignature(dspy.Signature):
    """Signature for implementation planning."""
    architecture = dspy.InputField()
    plan = dspy.OutputField(desc="Implementation plan")


class DeploymentHandlerSignature(dspy.Signature):
    """Signature for deployment handling."""
    service_name = dspy.InputField()
    service_code = dspy.InputField()
    deployment_plan = dspy.OutputField(desc="Deployment plan and configuration")


class InfrastructurePlannerSignature(dspy.Signature):
    """Signature for infrastructure planning."""
    architecture = dspy.InputField()
    infrastructure_plan = dspy.OutputField(desc="Infrastructure requirements and setup")


class UIDesignerSignature(dspy.Signature):
    """Signature for UI design."""
    feature = dspy.InputField()
    requirements = dspy.InputField()
    design = dspy.OutputField(desc="UI design specification")


class UsabilityTesterSignature(dspy.Signature):
    """Signature for usability testing."""
    ui_design = dspy.InputField()
    test_results = dspy.OutputField(desc="Usability test results and recommendations")


class PMAgentModule(dspy.Module):
    """DSPy module for the Project Management Agent."""
    
    def __init__(self):
        super().__init__()
        self.req_analyzer = dspy.ChainOfThought(RequirementsAnalyzerSignature)
        self.arch_designer = dspy.ChainOfThought(ArchitectureDesignerSignature)
        self.arch_finalizer = dspy.ChainOfThought(ArchitectureFinalizerSignature)
        self.feature_planner = dspy.ChainOfThought(FeaturePlannerSignature)

    def forward(self, agent_id: str, agent_role: str, task: Dict[str, Any], context: Dict[str, Any]):
        """Process a task with the appropriate module based on task type."""
        task_type = task.get("type", "")
        logger.info(f"PM Agent processing task: {task_type}")
        
        if task_type == "requirements_analysis":
            project_desc = task.get("description", "")
            result = self.req_analyzer(project_description=project_desc)
            # Parse the string result into a structured dict
            try:
                requirements = json.loads(result.requirements)
            except json.JSONDecodeError:
                # Fallback to returning as-is if not valid JSON
                requirements = {
                    "name": "Project",
                    "description": result.requirements[:100],
                    "requirements": [result.requirements]
                }
            return {"status": "success", "requirements": requirements}
        
        elif task_type == "architecture_design":
            requirements = task.get("requirements", {})
            result = self.arch_designer(requirements=json.dumps(requirements))
            try:
                architecture = json.loads(result.architecture)
            except json.JSONDecodeError:
                architecture = {
                    "name": "System Architecture",
                    "description": "Generated architecture",
                    "components": [{"name": "Default", "description": result.architecture[:100]}]
                }
            return architecture
        
        elif task_type == "architecture_finalization":
            initial_arch = task.get("initial_architecture", {})
            feedback = task.get("feedback", [])
            result = self.arch_finalizer(
                initial_architecture=json.dumps(initial_arch),
                feedback=json.dumps(feedback)
            )
            try:
                final_architecture = json.loads(result.final_architecture)
            except json.JSONDecodeError:
                final_architecture = initial_arch
                final_architecture["version"] = "1.0.0"  # Bump version to indicate finalization
            return final_architecture
        
        elif task_type == "feature_planning":
            architecture = task.get("architecture", {})
            requirements = task.get("requirements", {})
            result = self.feature_planner(
                architecture=json.dumps(architecture),
                requirements=json.dumps(requirements)
            )
            try:
                feature_plan = json.loads(result.feature_plan)
            except json.JSONDecodeError:
                feature_plan = {
                    "features": [{"name": "Default", "description": result.feature_plan[:100]}]
                }
            return {"status": "success", "feature_plan": feature_plan}
        
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}",
                "task": task
            }


class DevAgentModule(dspy.Module):
    """DSPy module for the Development Agent."""
    
    def __init__(self):
        super().__init__()
        self.code_impl = dspy.ChainOfThought(CodeImplementerSignature)
        self.code_reviewer = dspy.ChainOfThought(CodeReviewerSignature)
        self.arch_reviewer = dspy.ChainOfThought(ArchitectureReviewerSignature)
        self.impl_planner = dspy.ChainOfThought(ImplementationPlannerSignature)

    def forward(self, agent_id: str, agent_role: str, task: Dict[str, Any], context: Dict[str, Any]):
        """Process a task with the appropriate module based on task type."""
        task_type = task.get("type", "")
        logger.info(f"Dev Agent processing task: {task_type}")
        
        if task_type == "service_implementation":
            service_name = task.get("service_name", "")
            requirements = task.get("requirements", {})
            architecture = task.get("architecture", {})
            
            result = self.code_impl(
                service_name=service_name,
                requirements=json.dumps(requirements),
                architecture=json.dumps(architecture)
            )
            
            return {
                "status": "success",
                "service_name": service_name,
                "code": result.code
            }
        
        elif task_type == "code_review":
            code = task.get("code", "")
            result = self.code_reviewer(code=code)
            
            return {
                "status": "completed",
                "feedback": result.review
            }
        
        elif task_type == "architecture_review":
            architecture = task.get("architecture", {})
            result = self.arch_reviewer(architecture=json.dumps(architecture))
            
            try:
                review = json.loads(result.review)
            except json.JSONDecodeError:
                review = {
                    "strengths": ["Good overall design"],
                    "weaknesses": ["Need more details"],
                    "recommendations": [result.review]
                }
                
            return {
                "status": "success",
                "feedback": review
            }
        
        elif task_type == "implementation_planning":
            architecture = task.get("architecture", {})
            result = self.impl_planner(architecture=json.dumps(architecture))
            
            try:
                plan = json.loads(result.plan)
            except json.JSONDecodeError:
                plan = {
                    "phases": [
                        {
                            "name": "Implementation",
                            "tasks": [{"description": result.plan}]
                        }
                    ]
                }
                
            return {
                "status": "success",
                "plan": plan
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}"
            }


class DevOpsAgentModule(dspy.Module):
    """DSPy module for the DevOps Agent."""
    
    def __init__(self):
        super().__init__()
        self.deployment_handler = dspy.ChainOfThought(DeploymentHandlerSignature)
        self.infra_planner = dspy.ChainOfThought(InfrastructurePlannerSignature)
        self.arch_reviewer = dspy.ChainOfThought(ArchitectureReviewerSignature)  # Reusing from above

    def forward(self, agent_id: str, agent_role: str, task: Dict[str, Any], context: Dict[str, Any]):
        """Process a task with the appropriate module based on task type."""
        task_type = task.get("type", "")
        logger.info(f"DevOps Agent processing task: {task_type}")
        
        if task_type == "service_deployment":
            service_name = task.get("service_name", "")
            service_code = task.get("service_code", "")
            
            if not service_code and "implementation" in task:
                service_code = task["implementation"].get("code", "")
                
            result = self.deployment_handler(
                service_name=service_name, 
                service_code=service_code
            )
            
            try:
                deployment = json.loads(result.deployment_plan)
            except json.JSONDecodeError:
                deployment = {
                    "service": service_name,
                    "environment": "development",
                    "configs": [{"key": "main", "value": result.deployment_plan}]
                }
                
            return {
                "status": "success",
                "deployment": {
                    "service_name": service_name,
                    "version": "1.0.0",
                    "environment": "development",
                    "configs": deployment
                }
            }
        
        elif task_type == "infrastructure_planning":
            architecture = task.get("architecture", {})
            result = self.infra_planner(architecture=json.dumps(architecture))
            
            try:
                infrastructure = json.loads(result.infrastructure_plan)
            except json.JSONDecodeError:
                infrastructure = {
                    "resources": [{"type": "server", "description": result.infrastructure_plan}]
                }
                
            return {
                "status": "success",
                "infrastructure": infrastructure
            }
        
        elif task_type == "architecture_review":
            architecture = task.get("architecture", {})
            result = self.arch_reviewer(architecture=json.dumps(architecture))
            
            try:
                review = json.loads(result.review)
            except json.JSONDecodeError:
                review = {
                    "strengths": ["Deployable architecture"],
                    "weaknesses": ["Need more DevOps considerations"],
                    "recommendations": [result.review]
                }
                
            return {
                "status": "success",
                "feedback": review
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}"
            }


class UXAgentModule(dspy.Module):
    """DSPy module for the UX Agent."""
    
    def __init__(self):
        super().__init__()
        self.ui_designer = dspy.ChainOfThought(UIDesignerSignature)
        self.arch_reviewer = dspy.ChainOfThought(ArchitectureReviewerSignature)  # Reusing from above
        self.usability_tester = dspy.ChainOfThought(UsabilityTesterSignature)

    def forward(self, agent_id: str, agent_role: str, task: Dict[str, Any], context: Dict[str, Any]):
        """Process a task with the appropriate module based on task type."""
        task_type = task.get("type", "")
        logger.info(f"UX Agent processing task: {task_type}")
        
        if task_type == "ui_design":
            feature = task.get("feature", "")
            requirements = task.get("requirements", {})
            
            result = self.ui_designer(
                feature=feature,
                requirements=json.dumps(requirements)
            )
            
            try:
                design = json.loads(result.design)
            except json.JSONDecodeError:
                design = {
                    "feature": feature,
                    "components": [{"type": "screen", "description": result.design}]
                }
                
            return {
                "status": "success",
                "design": design
            }
        
        elif task_type == "architecture_review":
            architecture = task.get("architecture", {})
            result = self.arch_reviewer(architecture=json.dumps(architecture))
            
            try:
                review = json.loads(result.review)
            except json.JSONDecodeError:
                review_id = f"ux_arch_review_{hash(str(architecture))%10000000:x}"
                review = {
                    "id": review_id,
                    "ux_considerations": [result.review]
                }
                
            return review
        
        elif task_type == "usability_testing":
            ui_design = task.get("design", {})
            result = self.usability_tester(ui_design=json.dumps(ui_design))
            
            try:
                test_results = json.loads(result.test_results)
            except json.JSONDecodeError:
                test_results = {
                    "issues": [{"severity": "medium", "description": result.test_results}],
                    "recommendations": ["Improve usability based on test results"]
                }
                
            return {
                "status": "success",
                "test_results": test_results
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}"
            }
