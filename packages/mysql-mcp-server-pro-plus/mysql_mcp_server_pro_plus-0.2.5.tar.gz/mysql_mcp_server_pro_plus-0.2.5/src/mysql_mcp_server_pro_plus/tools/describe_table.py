from ..logger import logger


async def describe_table_tool(table_name: str, db_manager, security_validator) -> str:
    """Describe the structure of a table.

    Args:
        table_name: Name of the table to describe
        db_manager: Database manager instance
        security_validator: Security validator instance
    """
    try:
        logger.info(f"Describing table: {table_name}")

        if not db_manager or not security_validator:
            raise RuntimeError("Server not properly initialized")

        if not security_validator._is_valid_table_name(table_name):
            raise ValueError(f"Invalid table name: {table_name}")

        query = f"DESCRIBE `{table_name}`"
        result = await db_manager.execute_query(query)

        if result.has_results:
            lines = [",".join(result.columns)]
            for row in result.rows:
                lines.append(",".join(str(cell) for cell in row))
            return "\n".join(lines)
        else:
            return "No table structure information available"

    except Exception as e:
        logger.error(f"Error describing table {table_name}: {e}")
        return f"Error: {str(e)}"
