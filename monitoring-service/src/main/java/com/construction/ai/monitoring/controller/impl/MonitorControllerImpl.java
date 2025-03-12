package com.construction.ai.monitoring.controller.impl;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

import com.construction.ai.monitoring.controller.MonitorController;
import com.construction.ai.monitoring.models.HealthResponse;
import com.construction.ai.monitoring.models.ModelsResponse;
import com.construction.ai.monitoring.service.MonitorService;

import org.springframework.beans.factory.annotation.Autowired;

import io.swagger.v3.oas.annotations.tags.Tag;

@RestController
@Tag(name = "Ollama Monitoring API", description = "API endpoints for monitoring Ollama and microservices")
public class MonitorControllerImpl implements MonitorController {
	
	@Autowired
	private MonitorService monitorService;

	public ResponseEntity<ModelsResponse> getModels() {
		return ResponseEntity.ok(monitorService.getOllamaModels());
	}

	public ResponseEntity<HealthResponse> checkAllServicesHealth() {
		return ResponseEntity.ok(monitorService.checkAllServicesHealth());
	}
}
