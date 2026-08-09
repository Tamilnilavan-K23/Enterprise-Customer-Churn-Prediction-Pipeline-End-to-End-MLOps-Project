import great_expectations as gx
from typing import Tuple, List


def validate_telco_data(df) -> Tuple[bool, List[str]]:
    """
    Comprehensive data validation for the Telco Customer Churn dataset
    using Great Expectations 1.5.x.

    Returns:
        Tuple[bool, List[str]]:
            - True/False indicating whether all validations passed
            - List containing the failed expectation types
    """

    print("🔍 Starting data validation with Great Expectations...")

    # ============================================================
    # 1. CREATE GREAT EXPECTATIONS CONTEXT
    # ============================================================

    context = gx.get_context(mode="ephemeral")

    # ============================================================
    # 2. CREATE PANDAS DATA SOURCE
    # ============================================================

    data_source = context.data_sources.add_pandas(
        name="telco_pandas_source"
    )

    # Create a Data Asset for the DataFrame
    data_asset = data_source.add_dataframe_asset(
        name="telco_dataframe"
    )

    # Create a batch definition
    batch_definition = data_asset.add_batch_definition_whole_dataframe(
        name="telco_batch"
    )

    # Create the batch using the DataFrame
    batch = batch_definition.get_batch(
        batch_parameters={"dataframe": df}
    )

    # ============================================================
    # 3. CREATE EXPECTATION SUITE
    # ============================================================

    expectation_suite = context.suites.add(
        gx.core.expectation_suite.ExpectationSuite(
            name="telco_data_validation"
        )
    )

    # ============================================================
    # 4. SCHEMA VALIDATION - ESSENTIAL COLUMNS
    # ============================================================

    print("   📋 Validating schema and required columns...")

    required_columns = [
        "gender",
        "Partner",
        "Dependents",
        "PhoneService",
        "InternetService",
        "Contract",
        "tenure",
        "MonthlyCharges",
        "TotalCharges",
    ]

    for column in required_columns:
        expectation_suite.add_expectation(
            gx.expectations.ExpectColumnToExist(
                column=column
            )
        )

    # Customer identifier must not be null
    '''
    expectation_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="customerID"
        )
    )
    '''

    # ============================================================
    # 5. BUSINESS LOGIC VALIDATION
    # ============================================================

    print("   💼 Validating business logic constraints...")

    # Gender
    expectation_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="gender",
            value_set=["Male", "Female"],
        )
    )

    # Yes / No fields
    for column in [
        "Partner",
        "Dependents",
        "PhoneService",
    ]:
        expectation_suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeInSet(
                column=column,
                value_set=["Yes", "No"],
            )
        )

    # Contract types
    expectation_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="Contract",
            value_set=[
                "Month-to-month",
                "One year",
                "Two year",
            ],
        )
    )

    # Internet service types
    expectation_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="InternetService",
            value_set=[
                "DSL",
                "Fiber optic",
                "No",
            ],
        )
    )

    # ============================================================
    # 6. NUMERIC RANGE VALIDATION
    # ============================================================

    print("   📊 Validating numeric ranges and business constraints...")

    # Tenure >= 0
    expectation_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="tenure",
            min_value=0,
        )
    )

    # MonthlyCharges >= 0
    expectation_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="MonthlyCharges",
            min_value=0,
        )
    )

    # TotalCharges >= 0
    expectation_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="TotalCharges",
            min_value=0,
        )
    )

    # ============================================================
    # 7. STATISTICAL VALIDATION
    # ============================================================

    print("   📈 Validating statistical properties...")

    # Tenure maximum = 120 months
    expectation_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="tenure",
            min_value=0,
            max_value=120,
        )
    )

    # Monthly charges maximum = 200
    expectation_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="MonthlyCharges",
            min_value=0,
            max_value=200,
        )
    )

    # Critical numeric columns cannot be null
    expectation_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="tenure"
        )
    )

    expectation_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="MonthlyCharges"
        )
    )

    # ============================================================
    # 8. DATA CONSISTENCY
    # ============================================================

    print("   🔗 Validating data consistency...")

    # TotalCharges should generally be >= MonthlyCharges.
    #
    # We implement the original business rule manually because
    # the old PandasDataset pair expectation is no longer part
    # of the API being used here.
    print(df.dtypes)
    print(df["TotalCharges"].head(10))

    total_charges = df["TotalCharges"]
    monthly_charges = df["MonthlyCharges"]

    valid_comparisons = (
        total_charges.notna()
        & monthly_charges.notna()
    )

    if valid_comparisons.sum() > 0:

        comparison_success = (
            total_charges[valid_comparisons]
            >= monthly_charges[valid_comparisons]
        )

        comparison_rate = comparison_success.mean()

        if comparison_rate < 0.95:
            print(
                "   ⚠️ TotalCharges >= MonthlyCharges "
                f"check failed: {comparison_rate:.2%} "
                "of rows satisfy the condition."
            )

            pair_check_failed = True

        else:
            print(
                "   ✅ TotalCharges >= MonthlyCharges "
                f"check passed: {comparison_rate:.2%} "
                "of rows satisfy the condition."
            )

            pair_check_failed = False

    else:
        print(
            "   ⚠️ Unable to perform TotalCharges/"
            "MonthlyCharges comparison."
        )

        pair_check_failed = True

    # ============================================================
    # 9. VALIDATE EXPECTATION SUITE
    # ============================================================

    print("   ⚙️ Running complete validation suite...")

    validation_results = batch.validate(
        expectation_suite
    )

    # ============================================================
    # 10. PROCESS RESULTS
    # ============================================================

    failed_expectations = []

    for result in validation_results.results:

        if not result.success:

            expectation_type = (
                result.expectation_config.type
            )

            failed_expectations.append(
                expectation_type
            )

    # Add manual pair validation if it failed
    if pair_check_failed:
        failed_expectations.append(
            "TotalCharges >= MonthlyCharges (95% threshold)"
        )

    total_checks = len(validation_results.results) + 1

    passed_checks = (
        total_checks
        - len(failed_expectations)
    )

    failed_checks = (
        total_checks
        - passed_checks
    )

    # ============================================================
    # 11. FINAL RESULT
    # ============================================================

    overall_success = (
        validation_results.success
        and not pair_check_failed
    )

    if overall_success:

        print(
            f"✅ Data validation PASSED: "
            f"{passed_checks}/{total_checks} "
            "checks successful"
        )

    else:

        print(
            f"❌ Data validation FAILED: "
            f"{failed_checks}/{total_checks} "
            "checks failed"
        )

        print(
            f"   Failed expectations: "
            f"{failed_expectations}"
        )

    return overall_success, failed_expectations
