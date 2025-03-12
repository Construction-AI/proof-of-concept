package com.construction.ai.monitoring.service.services;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import com.construction.ai.monitoring.service.models.HealthResponse;
import com.construction.ai.monitoring.service.models.ModelInfo;
import com.construction.ai.monitoring.service.models.ModelsResponse;
import com.construction.ai.monitoring.service.models.ServiceHealth;
import com.construction.ai.monitoring.service.models.SingleServiceHealthResponse;

@Service
public class MonitorService {
    private static final Logger logger = LoggerFactory.getLogger(MonitorService.class);
    private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ISO_DATE_TIME;
    
	@Autowired
	private RestTemplate restTemplate;

	@Value("${service.ollama.url}")
	private String ollamaUrl;
	
	@Value("${service.qdrant.url}")
	private String qdrantUrl;
	
	@Value("${service.llamaindex.url}")
	private String llamaIndexUrl;
	
	@Value("${service.frontend.url}")
	private String frontendUrl;
	
	@Value("${service.gateway.url}")
	private String gatewayUrl;
		
	@Value("${health.endpoint.qdrant}")
	private String qdrantHealthEndpoint;
	
	@Value("${health.endpoint.llamaindex}")
	private String llamaIndexHealthEndpoint;
	
	@Value("${health.endpoint.frontend}")
	private String frontendHealthEndpoint;
	
	@Value("${health.endpoint.gateway}")
	private String gatewayHealthEndpoint;

	/*
	 * Get list of models available for download from Ollama
	 */
	public ModelsResponse getOllamaModels() {
        logger.info("Fetching Ollama models from {}", ollamaUrl + "/api/tags");
		try {
			ResponseEntity<Map<String, List<LinkedHashMap<String, Object>>>> response = restTemplate.exchange(
				ollamaUrl + "/api/tags",
				HttpMethod.GET,
				null,
				new ParameterizedTypeReference<Map<String, List<LinkedHashMap<String, Object>>>>() {}
			);

			if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                logger.debug("Received successful response from Ollama API with status: {}", response.getStatusCode());
				List<LinkedHashMap<String, Object>> modelsList = response.getBody().get("models");
				List<ModelInfo> models = new ArrayList<>();

				if (modelsList != null) {
                    logger.debug("Processing {} models from Ollama API", modelsList.size());
					for (LinkedHashMap<String, Object> model: modelsList) {
                        try {
                            Object sizeObj = model.get("size");
                            Long size = null;
                            if (sizeObj instanceof Integer) {
                                size = ((Integer) sizeObj).longValue();
                            } else if (sizeObj instanceof Long) {
                                size = (Long) sizeObj;
                            } else if (sizeObj != null) {
                                try {
                                    size = Long.valueOf(sizeObj.toString());
                                } catch (NumberFormatException e) {
                                    logger.warn("Failed to parse model size value '{}' for model '{}': {}", 
                                                sizeObj, model.get("name"), e.getMessage());
                                }
                            }
                            
                            models.add(ModelInfo.builder()
                                .name((String) model.get("name"))
                                .digest((String) model.get("digest"))
                                .size(size)
                                .modified((String) model.get("modified"))
                                .details(new HashMap<>(model))
                                .build()
                            );
                            logger.debug("Processed model: {}", model.get("name"));
                        } catch (Exception e) {
                            logger.error("Error processing model data: {}", e.getMessage(), e);
                        }
					}
				} else {
                    logger.warn("No models found in the Ollama API response");
                }

                logger.info("Successfully retrieved {} Ollama models", models.size());
				return ModelsResponse.builder().models(models).build();
			}
            logger.warn("Received non-OK response from Ollama API: {}", response.getStatusCode());
			return ModelsResponse.builder().models(Collections.emptyList()).build();
		} catch (RestClientException e) {
			logger.error("Error fetching Ollama models: {}", e.getMessage(), e);
			return ModelsResponse.builder().models(Collections.emptyList()).build();
		}
	}
	
	public SingleServiceHealthResponse checkSingleServiceHealthResponse(String serviceName, String url, String expectedResponse) {
		if (expectedResponse == null) {
			expectedResponse = "ok";
		}
        logger.info("Checking {} health at {}", serviceName, url);
		try {
			ResponseEntity<String> response = restTemplate.exchange(
				url,
				HttpMethod.GET,
				null,
				String.class
			);

			Map<String, Object> details = new HashMap<>();

			String status = response.getBody().contains(expectedResponse) ? "UP": "DOWN";

			details.put("response", response.getBody());

			return SingleServiceHealthResponse.builder()
				.service(serviceName)
				.status(status)
				.timestamp(LocalDateTime.now().format(FORMATTER))
				.details(details)
				.build();
		} catch (RestClientException e) {
			Map<String, Object> details = new HashMap<>();
			details.put("error", e.getMessage());
			logger.error("Error checking {} health: {}", serviceName, e.getMessage(), e);

			return SingleServiceHealthResponse.builder()
				.service(serviceName)
				.status("DOWN")
				.timestamp(LocalDateTime.now().format(FORMATTER))
				.details(details)
				.build();
		}
	}

	public HealthResponse checkAllServicesHealth() {
        logger.info("Checking health of all services");
		List<ServiceHealth> services = new ArrayList<>();
		boolean allUp = true;

        logger.debug("Checking Ollama health");
		SingleServiceHealthResponse ollamaHealthResponse = checkSingleServiceHealthResponse("Ollama", ollamaUrl, "Ollama is running");
		ServiceHealth ollamaHealth = new ServiceHealth(ollamaHealthResponse);
		services.add(ollamaHealth);
		if (!"Ollama is running".equals(ollamaHealth.getDetails().get("response"))) {
			allUp = false;
            logger.warn("Ollama service is DOWN");
		}
		
        logger.debug("Checking Qdrant health");
		SingleServiceHealthResponse qdrantHealthResponse = checkSingleServiceHealthResponse("Qdrant", qdrantUrl + qdrantHealthEndpoint, "healthz check passed");
		ServiceHealth qdrantHealth = new ServiceHealth(qdrantHealthResponse);
		services.add(qdrantHealth);
		if (!"healthz check passed".equals(qdrantHealth.getDetails().get("response"))) {
			allUp = false;
            logger.warn("Qdrant service is DOWN");
		}

        logger.debug("Checking LlamaIndex health");
		SingleServiceHealthResponse llamaindexHealthResponse = checkSingleServiceHealthResponse("llamaIndex", llamaIndexUrl + llamaIndexHealthEndpoint, "ok");
		ServiceHealth llamaIndexHealth = new ServiceHealth(llamaindexHealthResponse);
		services.add(llamaIndexHealth);
		if (!"UP".equals(llamaIndexHealth.getStatus())) {
			allUp = false;
            logger.warn("LlamaIndex service is DOWN");
		}

        logger.debug("Checking Frontend health");
		SingleServiceHealthResponse frontHealthResponse = checkSingleServiceHealthResponse("frontend", frontendUrl + frontendHealthEndpoint, "ok");
		ServiceHealth frontendHealth = new ServiceHealth(frontHealthResponse);
		services.add(frontendHealth);
		if (!"UP".equals(frontendHealth.getStatus())) {
			allUp = false;
            logger.warn("Frontend service is DOWN");
		}

        logger.debug("Checking Gateway health");
		SingleServiceHealthResponse gatewayHealthResponse = checkSingleServiceHealthResponse("gateway", gatewayUrl + gatewayHealthEndpoint, "ok");
		ServiceHealth gatewayHealth = new ServiceHealth(gatewayHealthResponse);
		services.add(gatewayHealth);
		if (!"UP".equals(gatewayHealth.getStatus())) {
			allUp = false;
            logger.warn("Gateway service is DOWN");
		}

		String overallStatus = allUp ? "UP": "DEGRADED";
        logger.info("Overall system health status: {}", overallStatus);

		return HealthResponse.builder()
			.status(overallStatus)
			.services(services)
			.timestamp(LocalDateTime.now().format(FORMATTER))
			.build();
	}
}