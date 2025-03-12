package com.construction.ai.monitoring.models;

import java.util.List;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "Response containing health status of services")
public class HealthResponse {
	@Schema(description = "Overall system health status")
	private String status;

	@Schema(description = "List of service health statuses")
	private List<ServiceHealth> services;

	@Schema(description = "Timestamp of health check")
	private String timestamp;
}
