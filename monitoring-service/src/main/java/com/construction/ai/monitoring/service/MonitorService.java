package com.construction.ai.monitoring.service;

import com.construction.ai.monitoring.models.HealthResponse;
import com.construction.ai.monitoring.models.ModelsResponse;
import com.construction.ai.monitoring.models.SingleServiceHealthResponse;

public interface MonitorService {
	/*
	 * Get list of models available for download from Ollama
	 */
	public ModelsResponse getOllamaModels();
	
	public SingleServiceHealthResponse checkSingleServiceHealthResponse(String serviceName, String url, String expectedResponse);

	public HealthResponse checkAllServicesHealth();
}