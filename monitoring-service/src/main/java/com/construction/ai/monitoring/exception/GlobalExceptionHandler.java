package com.construction.ai.monitoring.exception;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.client.RestClientException;
import org.springframework.web.context.request.WebRequest;

public interface GlobalExceptionHandler {
	
	@ExceptionHandler(RestClientException.class)
	public ResponseEntity<ErrorResponse> handleRestClientException(RestClientException ex, WebRequest request);

	@ExceptionHandler(Exception.class)
	public ResponseEntity<ErrorResponse> handleGenericException(RestClientException ex, WebRequest request);
}