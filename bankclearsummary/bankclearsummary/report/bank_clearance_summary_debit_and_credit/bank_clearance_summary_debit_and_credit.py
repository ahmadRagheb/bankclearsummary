# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import nowdate, getdate ,cint, flt
import datetime
def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns()
	data= get_entries(filters)
	# total_raw = [u'Total', None, None, None, None, None, total_credit, total_debit,general_total]
	# data.append(total_raw)
	return columns, data


def get_columns():
	return [
		_("Payment Document") + "::130",
		_("Payment Entry") + ":Dynamic Link/"+_("Payment Document")+":110",
		_("Posting Date") + ":Date:100",
		_("Cheque/Reference No") + "::120",
		_("Clearance Date") + ":Date:100",
		_("Against Account") + ":Link/Account:170",
		_("Debit") + ":Currency:120",
		_("Credit") + ":Currency:120",
		_("Amount") + ":Currency:120",

		# _("Total"),
	]

def get_conditions(filters):
	conditions = ""

	if filters.get("from_date"): conditions += " and posting_date>=%(from_date)s"
	if filters.get("to_date"): conditions += " and posting_date<=%(to_date)s"

	return conditions

def get_entries(filters):
	conditions = get_conditions(filters)

	journal_entries =  frappe.db.sql("""select "Journal Entry", jv.name, jv.posting_date,
		jv.cheque_no, jv.clearance_date, jvd.against_account,jvd.debit , jvd.credit, (jvd.debit - jvd.credit)
		from `tabJournal Entry Account` jvd, `tabJournal Entry` jv
		where jvd.parent = jv.name and jv.docstatus=1 and jvd.account = %(account)s {0}
		order by posting_date DESC, jv.name DESC""".format(conditions), filters, as_list=1)

	# total_journal =  frappe.db.sql("""select sum(jvd.debit - jvd.credit)
	# 	from `tabJournal Entry Account` jvd, `tabJournal Entry` jv
	# 	where jvd.parent = jv.name and jv.docstatus=1 and jvd.account = %(account)s {0}
	# 	order by posting_date DESC, jv.name DESC""".format(conditions), filters, as_list=1)


	payment_entries =  frappe.db.sql("""select "Payment Entry", name, posting_date,
		reference_no, clearance_date, party, if(paid_from!=%(account)s, received_amount, 0),if(paid_from=%(account)s, paid_amount, 0),
		 if(paid_from=%(account)s, paid_amount, received_amount)
		from `tabPayment Entry`
		where docstatus=1 and (paid_from = %(account)s or paid_to = %(account)s) {0}
		order by posting_date DESC, name DESC""".format(conditions), filters, as_list=1)

	# total_payment =  frappe.db.sql("""select sum(if(paid_from=%(account)s, paid_amount, received_amount))
	# 	from `tabPayment Entry` where docstatus=1 and (paid_from = %(account)s or paid_to = %(account)s) {0}
	# 	order by posting_date DESC, name DESC""".format(conditions), filters, as_list=1)

	# journal =total_journal[0]
	# payment =total_payment[0]

	# sub_journal = flt(journal[0])-flt(journal[1])
	# sub_payment = flt(payment[0])-flt(payment[1])

	# total_credit = flt(journal[0])+flt(payment[0])
	# total_debit = flt(journal[0])+flt(payment[1])

	# frappe.throw(str(sub_journal)+str(sub_payment))

	# general_total = abs(flt(sub_journal)+flt(sub_payment))

	# credit = flt(total_credit) + flt(received_amount)
	# debit = flt(total_debit) + flt(paid_amount)

	# total = credit-debit 

	return sorted(journal_entries + payment_entries, key=lambda k: k[2] or getdate(nowdate()))
	# general_total,total_credit,total_debit