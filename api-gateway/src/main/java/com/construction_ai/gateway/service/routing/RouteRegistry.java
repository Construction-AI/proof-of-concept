package com.construction_ai.gateway.service.routing;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.construction_ai.gateway.filter.LoggingFilter;
import com.construction_ai.gateway.model.RouteDefinition;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.core.io.ClassPathResource;

import jakarta.annotation.PostConstruct;

@Service
public class RouteRegistry {
	private final List<RouteDefinition> routes = new ArrayList<>();
	private final ObjectMapper objectMapper;
	private static final Logger logger = LoggerFactory.getLogger(LoggingFilter.class);

	@Autowired
	public RouteRegistry(ObjectMapper objectMapper) {
		this.objectMapper = objectMapper;
	}

	@PostConstruct
	public void loadRoutes() throws IOException {
		ClassPathResource resource = new ClassPathResource("routes/routes.json");
		RouteDefinition[] loadedRoutes = objectMapper.readValue(
			resource.getInputStream(), RouteDefinition[].class
		);
		this.routes.addAll(Arrays.asList(loadedRoutes));

		logger.info("Loaded {} routes", routes.size());
	}

	public List<RouteDefinition> getRoutes() {
		return this.routes;
	}
}
