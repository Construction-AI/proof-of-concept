package com.construction_ai.gateway.exception;

import org.springframework.http.HttpStatus;

public class GatewayException extends RuntimeException {
	private HttpStatus status = HttpStatus.INTERNAL_SERVER_ERROR;

	public GatewayException(String message) {
		super(message);
	}

	public GatewayException(String message, HttpStatus status) {
		super(message);
		this.status = status;
	}

	public HttpStatus getStatus() {
		return this.status;
	}
}
