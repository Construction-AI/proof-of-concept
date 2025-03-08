package com.construction_ai.gateway.service.forwarding;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Collections;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.StreamUtils;
import org.springframework.web.client.RestTemplate;

import com.construction_ai.gateway.model.RouteDefinition;
import com.construction_ai.gateway.model.ServiceInstance;
import com.construction_ai.gateway.service.discovery.ServiceRegistry;
import jakarta.servlet.http.HttpServletRequest;

@Service
public class RequestForwarder {
	private final RestTemplate restTemplate;
	private final ServiceRegistry serviceRegistry;
	// private final CircuitBreaker circuitBreaker;

	public RequestForwarder(
		RestTemplate restTemplate,
		ServiceRegistry serviceRegistry
		// CircuitBreaker circuitBreaker
	) {
		this.restTemplate = restTemplate;
		this.serviceRegistry = serviceRegistry;
		// this.circuitBreaker = circuitBreaker;
	}

	public ResponseEntity<String> forward(RouteDefinition route, HttpServletRequest request) {
		try {
			if ("welcome".equals(route.getServiceName())) {
				return ResponseEntity.ok("Welcome to Construction AI API Gateway");
			}
	

			ServiceInstance instances = serviceRegistry.getInstance(route.getServiceName());
	
			String targetUrl = buildTargetUrl(instances, request);

			HttpHeaders headers = copyRequestHeaders(request);
			String body = extractRequestBody(request);

			HttpEntity<String> httpEntity = new HttpEntity<>(body, headers);

			return restTemplate.exchange(
				targetUrl,
				HttpMethod.valueOf(request.getMethod()),
				httpEntity,
				String.class
			);
		} catch (Exception e) {
			return ResponseEntity.status(500).body("Internal Server Error");
		}
	}

	private String buildTargetUrl(ServiceInstance instance, HttpServletRequest request) {
		String requestUri = request.getRequestURI();
		String queryString = request.getQueryString();

		StringBuilder targetUrl = new StringBuilder(instance.getUrl());
		targetUrl.append(requestUri);

		if (queryString != null && !queryString.isEmpty()) {
			targetUrl.append("?").append(queryString);
		}

		return targetUrl.toString();
	}

	private HttpHeaders copyRequestHeaders(HttpServletRequest request) {
		HttpHeaders headers = new HttpHeaders();
		Collections.list(
			request.getHeaderNames()
		).forEach(
			headerName -> {
				headers.set(headerName, request.getHeader(headerName));
			}
		);

		headers.remove("host");
		return headers;
	}

	private String extractRequestBody(HttpServletRequest request) throws IOException {
		if (request.getContentLength() <= 0) {
			return null;
		}
		return StreamUtils.copyToString(request.getInputStream(), StandardCharsets.UTF_8);
	}
}
