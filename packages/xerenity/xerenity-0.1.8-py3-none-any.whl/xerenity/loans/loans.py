import csv


class Loans:

    def __init__(self, connection):
        self.con = connection

    def list_all(self, bank_names: list = None):
        """
        Retirna la lista de creditos del usuario
        :return:
        """

        return self.con.list_loans(bank_names=bank_names)

    def create_loan(self,
                    start_date: str,
                    bank: str,
                    number_of_payments: int,
                    original_balance: float,
                    periodicity: str,
                    interest_rate: float,
                    type: str,
                    days_count: str = None,
                    grace_type: str = None,
                    grace_period: int = None,
                    min_period_rate: str = None,
                    loan_identifier: str = None,
                    ):
        """
        Crea un credito en Xerenity
        :param start_date:
        :param bank:
        :param number_of_payments:
        :param original_balance:
        :param periodicity:
        :param interest_rate:
        :param type:
        :param days_count:
        :param grace_type:
        :param grace_period:
        :param min_period_rate:
        :param loan_identifier:
        :return:
        """
        return self.con.create_loan(
            start_date=start_date,
            bank=bank,
            number_of_payments=number_of_payments,
            original_balance=original_balance,
            periodicity=periodicity,
            interest_rate=interest_rate,
            type=type,
            days_count=days_count,
            grace_period=grace_period,
            grace_type=grace_type,
            min_period_rate=min_period_rate,
            loan_identifier=loan_identifier
        )

    def create_from_file(self, file_dir):
        """
        Crear lista de creditos desde archivo
        :return:
        """
        # Open the CSV file
        results=[]
        with open(file_dir, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)

            # Get the header row (first row)
            headers = next(reader)

            # Convert each subsequent row to dictionary
            for row_num, row in enumerate(reader, start=2):  # Start at 2 since we skipped header
                # Convert list to dictionary using zip
                row_dict = dict(zip(headers, row))

                # Remove empty values (empty strings, None, whitespace-only)
                cleaned_dict = {k: v for k, v in row_dict.items() if v and v.strip()}

                results.append(self.create_loan(**cleaned_dict))


        return results
