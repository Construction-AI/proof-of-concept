package com.construction.ai.monitoring.exception;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ErrorResponse {
	private String timestamp;
	private String status;
	private String message;
	private String path;
}
