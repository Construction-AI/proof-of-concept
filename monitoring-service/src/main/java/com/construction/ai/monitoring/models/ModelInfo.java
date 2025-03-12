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
@Schema(description = "Model information")
public class ModelInfo {
	@Schema(description = "Name of the model")
	private String name;

	@Schema(description = "Model size in bytes")
	private Long size;

	@Schema(description = "Model digest")
	private String digest;

	@Schema(description = "Model modification timestamp")
	private String modified;

	@Schema(description = "Additional model details")
	private Map<String, Object> details;
}
