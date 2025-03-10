package com.construction_ai.gateway.service.discovery;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import javax.management.ServiceNotFoundException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

import com.construction_ai.gateway.controller.GatewayController;
import com.construction_ai.gateway.model.ServiceInstance;
import com.fasterxml.jackson.databind.ObjectMapper;

import jakarta.annotation.PostConstruct;

@Service
public class ServiceRegistry {
	private final Map<String, ServiceInstance> serviceInstances = new ConcurrentHashMap<>();
	private final ObjectMapper objectMapper;
	private static final Logger logger = LoggerFactory.getLogger(GatewayController.class);

	public ServiceRegistry(ObjectMapper objectMapper) {
		this.objectMapper = objectMapper;
	}
	
	@PostConstruct
	public void loadServices() throws IOException {
		ClassPathResource resource =  new ClassPathResource("routes/services.json");
		ServiceInstance[] loadedServices = objectMapper.readValue(
			resource.getInputStream(), ServiceInstance[].class
		);
		for (ServiceInstance service : loadedServices) {
			serviceInstances.put(service.getName(), service);
		}

		logger.info("Loaded {} services", serviceInstances.size());
	}

	public ServiceInstance getInstance(String serviceName) throws ServiceNotFoundException {
        ServiceInstance instance = serviceInstances.get(serviceName);
		if (instance == null) {
			throw new ServiceNotFoundException("Service not found: " + serviceName);
		}
        return instance;
    }

	public void printServices() {
		logger.info("Accessible services: ");
		for (Map.Entry<String, ServiceInstance> entry : serviceInstances.entrySet()) {
			logger.info("Service Name: {}, Service Instance: {}", entry.getKey(), entry.getValue());
		}
	}
}
