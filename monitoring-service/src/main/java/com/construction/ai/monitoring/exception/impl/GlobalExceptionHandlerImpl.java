package com.construction.ai.monitoring.exception.impl;

import java.time.LocalDateTime;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.client.RestClientException;
import org.springframework.web.context.request.WebRequest;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

import com.construction.ai.monitoring.exception.ErrorResponse;
import com.construction.ai.monitoring.exception.GlobalExceptionHandler;

@ControllerAdvice
public class GlobalExceptionHandlerImpl extends ResponseEntityExceptionHandler implements GlobalExceptionHandler {
	
	public ResponseEntity<ErrorResponse> handleRestClientException(RestClientException ex, WebRequest request) {
		ErrorResponse errorResponse = new ErrorResponse(
			LocalDateTime.now().toString(),
			"Service Communication Error",
			ex.getMessage(),
			request.getDescription(false)
		);
		return new ResponseEntity<>(errorResponse, HttpStatus.SERVICE_UNAVAILABLE);
	}

	public ResponseEntity<ErrorResponse> handleGenericException(RestClientException ex, WebRequest request) {
		ErrorResponse errorResponse = new ErrorResponse(
			LocalDateTime.now().toString(),
			"Internal Server Error",
			ex.getMessage(),
			request.getDescription(false)
		);
		return new ResponseEntity<>(errorResponse, HttpStatus.INTERNAL_SERVER_ERROR);
	}
}

