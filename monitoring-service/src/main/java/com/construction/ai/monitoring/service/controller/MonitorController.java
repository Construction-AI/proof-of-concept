package com.construction.ai.monitoring.service.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import com.construction.ai.monitoring.service.models.HealthResponse;
import com.construction.ai.monitoring.service.models.ModelsResponse;
import com.construction.ai.monitoring.service.services.MonitorService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;

@RestController
@Tag(name = "Ollama Monitoring API", description = "API endpoints for monitoring Ollama and microservices")
public class MonitorController {
	@Autowired
	private MonitorService monitorService;

	@Operation(
		summary = "Get global models",
		description = "Retrieves a list models available locally"
	)
	@ApiResponses(
		value = {
			@ApiResponse(
				responseCode = "200",
				description = "Successfully retrieved global models",
				content = @Content(
					schema = @Schema(implementation = ModelsResponse.class)
				)
			),
			@ApiResponse(
				responseCode = "500",
				description = "Internal server error",
				content = @Content
			)
		}
	)
	@GetMapping("/models")
	public ResponseEntity<ModelsResponse> getModels() {
		return ResponseEntity.ok(monitorService.getOllamaModels());
	}

	@Operation(
		summary = "Check all services health",
		description = "Checks the health of all microservices in system"
	)
	@ApiResponses(
		value = {
			@ApiResponse(
				responseCode = "200",
				description = "Successfully checked all services health",
				content = @Content(
					schema = @Schema(implementation = HealthResponse.class)
				)
			),
			@ApiResponse(
				responseCode = "500",
				description = "Internal server error",
				content = @Content
			)
		}
	)
	@GetMapping("/health/services")
	public ResponseEntity<HealthResponse> checkAllServicesHealth() {
		return ResponseEntity.ok(monitorService.checkAllServicesHealth());
	}
}
