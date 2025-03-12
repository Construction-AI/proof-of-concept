package com.construction.ai.monitoring.exception;

import java.time.LocalDateTime;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.client.RestClientException;
import org.springframework.web.context.request.WebRequest;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@ControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {
	
	@ExceptionHandler(RestClientException.class)
	public ResponseEntity<ErrorResponse> handleRestClientException(RestClientException ex, WebRequest request) {
		ErrorResponse errorResponse = new ErrorResponse(
			LocalDateTime.now().toString(),
			"Service Communication Error",
			ex.getMessage(),
			request.getDescription(false)
		);
		return new ResponseEntity<>(errorResponse, HttpStatus.SERVICE_UNAVAILABLE);
	}

	@ExceptionHandler(Exception.class)
	public ResponseEntity<ErrorResponse> handleGenericException(RestClientException ex, WebRequest request) {
		ErrorResponse errorResponse = new ErrorResponse(
			LocalDateTime.now().toString(),
			"Internal Server Error",
			ex.getMessage(),
			request.getDescription(false)
		);
		return new ResponseEntity<>(errorResponse, HttpStatus.INTERNAL_SERVER_ERROR);
	}

	@Data
	@NoArgsConstructor
	@AllArgsConstructor
	public static class ErrorResponse {
		private String timestamp;
		private String status;
		private String message;
		private String path;
	}
}
