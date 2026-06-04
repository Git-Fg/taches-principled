//! Smoke tests for the input/output schemas.

use crate::schema::{ExecuteInput, WrapperResultEnvelope};

#[test]
fn execute_input_rejects_unknown_fields() {
    let value = serde_json::json!({
        "prompt": "hello",
        "bogus_extra_field": "should be rejected"
    });
    let parsed: Result<ExecuteInput, _> = serde_json::from_value(value);
    assert!(
        parsed.is_err(),
        "deny_unknown_fields should reject unknown fields at the serde level"
    );
}

#[test]
fn wrapper_result_envelope_schema_has_additional_properties_false() {
    let schema = rmcp::schemars::schema_for!(WrapperResultEnvelope);
    let json = serde_json::to_value(&schema).unwrap();
    let additional = json.get("additionalProperties");
    assert_eq!(
        additional,
        Some(&serde_json::json!(false)),
        "WrapperResultEnvelope schema must have additionalProperties: false. \
         Actual schema: {json}"
    );
}
