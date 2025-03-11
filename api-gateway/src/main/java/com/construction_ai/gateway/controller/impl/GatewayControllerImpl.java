package com.construction_ai.gateway.controller.impl;

import java.time.Instant;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.construction_ai.gateway.controller.GatewayController;
import com.construction_ai.gateway.exception.RouteNotFoundException;
import com.construction_ai.gateway.model.ApiResponse;
import com.construction_ai.gateway.model.RouteDefinition;
import com.construction_ai.gateway.service.forwarding.RequestForwarder;
import com.construction_ai.gateway.service.routing.RequestRouter;

import jakarta.servlet.http.HttpServletRequest;

@RestController
public class GatewayControllerImpl implements GatewayController {
	private final RequestRouter router;
	private final RequestForwarder forwarder;

	@Autowired
	public GatewayControllerImpl(RequestRouter router, RequestForwarder forwarder) {
		this.router = router;
		this.forwarder = forwarder;
	}

	@RequestMapping("/**")
	public ResponseEntity<?> handleRequest(HttpServletRequest request) {
		long startTime = System.currentTimeMillis();

		try {
			logger.info("Received request: {} {}", request.getMethod(), request.getRequestURI());

			RouteDefinition route = router.determineRoute(request);
			logger.info("Route found: {}, service: {}", route.getId(), route.getServiceName());

			// Forward request
			ResponseEntity<String> serviceResponse = forwarder.forward(route, request);

			long duration = System.currentTimeMillis() - startTime;
			logger.info("Request completed in {}ms", duration);

			logger.info("Service response: {}", serviceResponse.getBody());

			return serviceResponse;
		} catch (RouteNotFoundException e) {
			logger.warn("No route found for {}: {}", request.getRequestURI(), e.getMessage());
			return ResponseEntity.notFound().build();
		}
		catch (Exception e) {
			logger.error("Error processing request", e);
			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(new ApiResponse<>(false, null, "Internal gateway error", Instant.now().toString()));
		}
	}
}
