package com.construction.ai.monitoring.models;

import java.util.Map;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "Response for a single service health check")
public class SingleServiceHealthResponse {
	@Schema(description = "Service health status", example = "UP, DOWN")
	private String status;

	@Schema(description = "Service name")
	private String service;

	@Schema(description = "Timestamp of health check")
	private String timestamp;

	@Schema(description = "Additional health details if available")
	private Map<String, Object> details;
}
