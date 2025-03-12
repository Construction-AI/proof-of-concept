package com.construction.ai.monitoring.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;

import com.construction.ai.monitoring.models.HealthResponse;
import com.construction.ai.monitoring.models.ModelsResponse;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;

public interface MonitorController {
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
	public ResponseEntity<ModelsResponse> getModels();

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
	public ResponseEntity<HealthResponse> checkAllServicesHealth();
}
