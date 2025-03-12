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
@Schema(description = "Response containing list of models")
public class ModelsResponse {
	@Schema(description = "List of available models")
	private List<ModelInfo> models;
}
