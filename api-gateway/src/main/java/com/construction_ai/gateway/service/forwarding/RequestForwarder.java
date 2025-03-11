package com.construction_ai.gateway.service.forwarding;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.zip.GZIPInputStream;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.util.StreamUtils;

import com.construction_ai.gateway.model.RouteDefinition;
import com.construction_ai.gateway.model.ServiceInstance;
import jakarta.servlet.http.HttpServletRequest;

public interface RequestForwarder {
	static final Logger logger = LoggerFactory.getLogger(RequestForwarder.class);

	public ResponseEntity<String> forward(RouteDefinition route, HttpServletRequest request);

	default String buildTargetUrl(ServiceInstance instance, HttpServletRequest request) {
		String requestUri = request.getRequestURI();
		String queryString = request.getQueryString();

		StringBuilder targetUrl = new StringBuilder(instance.getUrl());
		targetUrl.append(requestUri);

		if (queryString != null && !queryString.isEmpty()) {
			targetUrl.append("?").append(queryString);
		}

		return targetUrl.toString();
	}

	default HttpHeaders copyRequestHeaders(HttpServletRequest request) {
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

	default String extractRequestBody(HttpServletRequest request) throws IOException {
		if (request.getContentLength() <= 0) {
			return null;
		}
		return StreamUtils.copyToString(request.getInputStream(), StandardCharsets.UTF_8);
	}

	default boolean isGzipEncoded(HttpHeaders headers) {
		String contentEncoding = headers.getFirst("Content-Encoding");
		return contentEncoding != null && contentEncoding.toLowerCase().contains("gzip");
	}

	default String decompressGzip(byte[] compressedData) throws IOException {
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
