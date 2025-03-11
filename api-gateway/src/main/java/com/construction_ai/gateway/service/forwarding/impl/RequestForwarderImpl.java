package com.construction_ai.gateway.service.forwarding.impl;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

import javax.management.ServiceNotFoundException;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.construction_ai.gateway.model.RouteDefinition;
import com.construction_ai.gateway.model.ServiceInstance;
import com.construction_ai.gateway.service.discovery.ServiceRegistry;
import com.construction_ai.gateway.service.forwarding.RequestForwarder;

import jakarta.servlet.http.HttpServletRequest;

@Service
public class RequestForwarderImpl implements RequestForwarder {
	private final RestTemplate restTemplate;
	private final ServiceRegistry serviceRegistry;

	public RequestForwarderImpl(
		RestTemplate restTemplate,
		ServiceRegistry serviceRegistry
	) {
		this.restTemplate = restTemplate;
		this.serviceRegistry = serviceRegistry;
	}

	public ResponseEntity<String> forward(RouteDefinition route, HttpServletRequest request) {
		try {
			if ("welcome".equals(route.getServiceName())) {
				return ResponseEntity.ok("Welcome to Construction AI API Gateway");
			}

			serviceRegistry.printServices();
	
			ServiceInstance instance = serviceRegistry.getInstance(route.getServiceName());

			String targetUrl = buildTargetUrl(instance, request);

			logger.info("Target URL: {}", targetUrl);
			
			HttpHeaders headers = copyRequestHeaders(request);
			String body = extractRequestBody(request);

			logger.info("Request Body: {}", body);

			HttpEntity<String> httpEntity = new HttpEntity<>(body, headers);
			logger.info("Forwarding request to: {}", targetUrl);

			ResponseEntity<byte[]> rawResponse = restTemplate.exchange(
				targetUrl,
				HttpMethod.valueOf(request.getMethod()),
				httpEntity,
				byte[].class
			);

			HttpHeaders responseHeaders = new HttpHeaders();
			responseHeaders.putAll(rawResponse.getHeaders());

			if (isGzipEncoded(responseHeaders)) {
				try {
					String decompressedBody = decompressGzip(rawResponse.getBody());
					responseHeaders.remove("Content-Encoding");
					return new ResponseEntity<>(decompressedBody, responseHeaders, rawResponse.getStatusCode());
				} catch (IOException e) {
					System.err.println("Failed to decompress the response: " + e.getMessage());
				} 
			}

			String responseBody = rawResponse.getBody() != null ? new String(rawResponse.getBody(), StandardCharsets.UTF_8): null;
			return new ResponseEntity<>(responseBody, responseHeaders, rawResponse.getStatusCode());
		} 
		catch (ServiceNotFoundException e) {
			return ResponseEntity.status(404).body("Service Not Found");
		}
		catch (Exception e) {
			return ResponseEntity.status(500).body("Internal Server Error");
		}
	}
 }
