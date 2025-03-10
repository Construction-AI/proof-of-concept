package com.construction_ai.gateway.service.forwarding;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.zip.GZIPInputStream;

import javax.management.ServiceNotFoundException;

import org.apache.catalina.connector.Request;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
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
	private static final Logger logger = LoggerFactory.getLogger(RequestForwarder.class);

	public RequestForwarder(
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

	private boolean isGzipEncoded(HttpHeaders headers) {
		String contentEncoding = headers.getFirst("Content-Encoding");
		return contentEncoding != null && contentEncoding.toLowerCase().contains("gzip");
	}

	private String decompressGzip(byte[] compressedData) throws IOException {
		if (compressedData == null) {
			return null;
		}

		try (
			ByteArrayInputStream bis = new ByteArrayInputStream(compressedData);
			GZIPInputStream gis = new GZIPInputStream(bis);
			ByteArrayOutputStream bos = new ByteArrayOutputStream())
		{
			byte[] buffer = new byte[1024];
			int len;
			while ((len = gis.read(buffer)) > 0) {
				bos.write(buffer, 0, len);
			}	

			return bos.toString("UTF-8");
		}		
	}
 }
