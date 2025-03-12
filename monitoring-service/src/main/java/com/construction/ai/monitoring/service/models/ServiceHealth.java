package com.construction.ai.monitoring.service.models;

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
@Schema(description = "Health status of a service")
public class ServiceHealth {

	public ServiceHealth(SingleServiceHealthResponse healthResponse) {
		this.serviceName = healthResponse.getService();
		this.status = healthResponse.getStatus();
		this.details = healthResponse.getDetails();
	}

	@Schema(description = "Name of the service")
	private String serviceName;

	@Schema(description = "Status of the service")
	private String status;

	@Schema(description = "Additional health details if available")
	private Map<String, Object> details;
}