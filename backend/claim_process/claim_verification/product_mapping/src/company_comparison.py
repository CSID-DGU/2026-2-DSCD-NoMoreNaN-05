"""Keep the chosen input company field explicit; never silently switch fields."""
def company_field(row):
    return row.get('comparison_company_field','manufacturer_name')


def company_values(row):
    field=company_field(row)
    values=[row[field]] if row.get(field) else []
    for observation in row.get('identity_observations',[]):
        observed_field=observation.get('field','manufacturer_name')
        if observed_field==field and observation.get('value'):
            values.append(observation['value'])
    return values
