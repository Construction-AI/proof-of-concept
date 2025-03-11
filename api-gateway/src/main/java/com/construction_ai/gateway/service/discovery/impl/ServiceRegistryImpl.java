package com.construction_ai.gateway.service.discovery.impl;

import java.io.IOException;
import java.util.Map;

import javax.management.ServiceNotFoundException;

import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

import com.construction_ai.gateway.model.ServiceInstance;
import com.construction_ai.gateway.service.discovery.ServiceRegistry;
import com.fasterxml.jackson.databind.ObjectMapper;

import jakarta.annotation.PostConstruct;

@Service
public class ServiceRegistryImpl implements ServiceRegistry {
	private final ObjectMapper objectMapper;

	public ServiceRegistryImpl(ObjectMapper objectMapper) {
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
