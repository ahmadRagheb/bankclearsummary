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
	data, total, total2, total3= get_entries(filters)
	# total_raw = [u'Total', None, None, None, None, None, total_credit, total_debit,general_total]
	# data.append(total_raw)
	# frappe.msgprint(str(total))
	total_raw = [u'Total', None, None, None, None, None, total3, total2, total]
	data.append(total_raw)
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

	payment_entries =  frappe.db.sql("""select "Payment Entry", name, posting_date,
		reference_no, clearance_date, party, if(paid_from!=%(account)s, received_amount, 0),if(paid_from=%(account)s, -paid_amount, 0),
		 if(paid_from=%(account)s, -paid_amount, received_amount)
		from `tabPayment Entry`
		where docstatus=1 and (paid_from = %(account)s or paid_to = %(account)s) {0}
		order by posting_date DESC, name DESC""".format(conditions), filters, as_list=1)

	result = sorted(journal_entries + payment_entries, key=lambda k: k[2] or getdate(nowdate()))
	cleand = [flt(x[-1]) for x in result]
	cleand_2 = [flt(x[-2]) for x in result]
	cleand_3 = [flt(x[-3]) for x in result]
	total = sum(cleand)
	total2 = sum(cleand_2)
	total3 = sum(cleand_3)

	for i, record in enumerate(result):
		del result[i][-1]
		result[i].append(0)

	return result,total,total2,total3
