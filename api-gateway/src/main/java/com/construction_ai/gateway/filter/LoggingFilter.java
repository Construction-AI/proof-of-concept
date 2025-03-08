package com.construction_ai.gateway.filter;

import org.slf4j.LoggerFactory;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.web.util.ContentCachingResponseWrapper;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;
import org.slf4j.Logger;

@Component
@Order(1)
public class LoggingFilter extends OncePerRequestFilter {
	private static final Logger logger = LoggerFactory.getLogger(LoggingFilter.class);

	@Override
	protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain) throws IOException, ServletException {
		// Log request
		logger.info("Request: {} {} from {}", request.getMethod(), request.getRequestURI(), request.getRemoteAddr());

		// Wrap the response to capture status
		ContentCachingResponseWrapper responseWrapper = new ContentCachingResponseWrapper(response);

		long startTime = System.currentTimeMillis();

		try {
			filterChain.doFilter(request, responseWrapper);
		} finally {
			// Log response
			long duration = System.currentTimeMillis() - startTime;
			logger.info("Response {} {} took {}ms", request.getMethod(), request.getRequestURI(), duration);

			responseWrapper.copyBodyToResponse();
		}
	}
}