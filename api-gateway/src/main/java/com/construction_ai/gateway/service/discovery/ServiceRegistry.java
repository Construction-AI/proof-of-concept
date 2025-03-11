package com.construction_ai.gateway.service.discovery;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import javax.management.ServiceNotFoundException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.construction_ai.gateway.controller.GatewayController;
import com.construction_ai.gateway.model.ServiceInstance;

public interface ServiceRegistry {
	final Map<String, ServiceInstance> serviceInstances = new ConcurrentHashMap<>();
	static final Logger logger = LoggerFactory.getLogger(GatewayController.class);
	public void loadServices() throws IOException;
	public ServiceInstance getInstance(String serviceName) throws ServiceNotFoundException;
	public void printServices();
}
