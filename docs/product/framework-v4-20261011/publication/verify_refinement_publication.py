#!/usr/bin/env python3
"""Fail-closed, offline verification of Imprana's append-only Linear refinement."""
import argparse
import copy
import csv
import hashlib
import itertools
import json
import re
from pathlib import Path

EXPECTED_COUNTS={'epic':54,'story':368,'task':1131}
EXPECTED_TOTAL=1553
EXPECTED_TASK_EDGES=779
PUBLICATION=re.compile(r'<!-- imprana:bundle-v4\.2:(epic|story|task):([^ ]+):20261011 -->')
TASK_PUBLICATION=re.compile(r'<!-- imprana:task-execution-refinement:([^ ]+):2026-10-11:v1 -->')
CANONICAL=re.compile(r'^<!-- imprana:(epic|story|task):([^ ]+) -->')
ONLY_NORMALIZATIONS={'publication_comment_heading_blankline','remove_single_final_lf','outside_fence_blankline_collapse','table_separator_three_to_two_dashes','table_trailing_cell_two_to_one_spaces','specific_missing_context_bracket_escape','leading_bold_code_emdash_heading','roadmap_exact_four_column_alignment_serialization','observed_three_supplement_heading_code_serialization','observed_empty_nfr08_source_label_space','observed_fixed_supplement_heading_code_serialization','observed_exact_empty_source_label_space'}
ROADMAP_DOCUMENT='41cf9cd4-17ef-4ebb-8f59-5a26504b2d5e'
OBSERVED_HEADING_IDS={'APL-545','APL-531','APL-535'}
OBSERVED_FIXED_HEADING_IDS={'APL-545', 'APL-478', 'APL-514', 'APL-575', 'APL-633', 'APL-337', 'APL-535', 'APL-519', 'APL-523', 'APL-526', 'APL-420', 'APL-457', 'APL-500', 'APL-685', 'APL-485', 'APL-379', 'APL-403', 'APL-628', 'APL-531'}
OBSERVED_EMPTY_LABEL_IDS={'APL-1832','APL-1837','APL-1839'}
FIXED_HEADING_SERIALIZATIONS={
    '**`AC-FR-ACC-007-003`: classify existing plan enrichment separately**':'`AC-FR-ACC-007-003`**: classify existing plan enrichment separately**',
    '**Proposed verification duty on existing `TASK-FR-AI-002-03` — Ambiguity review and unsupported-commitment qualification**':'**Proposed verification duty on existing** `TASK-FR-AI-002-03` **— Ambiguity review and unsupported-commitment qualification**',
    '**Proposed verification duty on existing `TASK-FR-AI-004-03` — Sample diff and destructive-proposal qualification**':'**Proposed verification duty on existing** `TASK-FR-AI-004-03` **— Sample diff and destructive-proposal qualification**',
    '**`AC-FR-DQ-001-001`: classify existing plan enrichment separately**':'`AC-FR-DQ-001-001`**: classify existing plan enrichment separately**',
    '**`AC-FR-DQ-005-001`: classify existing plan enrichment separately**':'`AC-FR-DQ-005-001`**: classify existing plan enrichment separately**',
    '**Proposed verification duty on existing `TASK-FR-DQ-001-03` — Quality editor and versioned failure qualification**':'**Proposed verification duty on existing** `TASK-FR-DQ-001-03` **— Quality editor and versioned failure qualification**',
    '**Proposed verification duty on existing `TASK-FR-INT-005-03` — Review migration notice and compatibility evidence before release**':'**Proposed verification duty on existing** `TASK-FR-INT-005-03` **— Review migration notice and compatibility evidence before release**',
    '**Proposed verification duty on existing `TASK-FR-MIG-003-03` — Critical variance cutover decision gate**':'**Proposed verification duty on existing** `TASK-FR-MIG-003-03` **— Critical variance cutover decision gate**',

    '**Proposed verification duty on existing `TASK-FR-PLN-006-03` — Readiness matrix and resolvable activation errors**':'**Proposed verification duty on existing** `TASK-FR-PLN-006-03` **— Readiness matrix and resolvable activation errors**',
    '**Proposed verification duty on existing `TASK-FR-PRG-006-03` — Partner acceptance and correction workflow**':'**Proposed verification duty on existing** `TASK-FR-PRG-006-03` **— Partner acceptance and correction workflow**',
    '**Proposed verification duty on existing `TASK-FR-SEC-011-03` — Approved notification and response exercise**':'**Proposed verification duty on existing** `TASK-FR-SEC-011-03` **— Approved notification and response exercise**',
    '**Proposed verification duty on existing `TASK-FR-TEN-002-03` — Unit/project move preview and qualification**':'**Proposed verification duty on existing** `TASK-FR-TEN-002-03` **— Unit/project move preview and qualification**',

    '**`AC-FR-UX-004-001`: classify existing plan enrichment separately**':'`AC-FR-UX-004-001`**: classify existing plan enrichment separately**',

    '**Proposed verification duty on existing `TASK-FR-WFL-001-03` — Workflow designer and stage-review qualification**':'**Proposed verification duty on existing** `TASK-FR-WFL-001-03` **— Workflow designer and stage-review qualification**',
    '**Proposed verification duty on existing `TASK-FR-WFL-003-03` — Actionable returned-work comparison and tests**':'**Proposed verification duty on existing** `TASK-FR-WFL-003-03` **— Actionable returned-work comparison and tests**',

    '**Proposed verification duty on existing `TASK-US-PT-01-03` — Unvetted listing and late-decision review**':'**Proposed verification duty on existing** `TASK-US-PT-01-03` **— Unvetted listing and late-decision review**',
    '**Proposed verification duty on existing `TASK-US-VC-04-03` — Three-scenario editor and oracle fixtures**':'**Proposed verification duty on existing** `TASK-US-VC-04-03` **— Three-scenario editor and oracle fixtures**',

    '**`AC-FR-WFL-007-002`: classify existing plan enrichment separately**':'`AC-FR-WFL-007-002`**: classify existing plan enrichment separately**',
    '**`AC-FR-WFL-008-001`: classify existing plan enrichment separately**':'`AC-FR-WFL-008-001`**: classify existing plan enrichment separately**',
    '**`AC-US-RT-05-001`: classify existing plan enrichment separately**':'`AC-US-RT-05-001`**: classify existing plan enrichment separately**',

}
EMPTY_NFR08_SOURCE_LINE='**Required source:** `NFR-08`; bounded contribution anchors `AC-NFR-08-004`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: '
OBSERVED_ALL_EMPTY_LABEL_IDS={'APL-1200', 'APL-1219', 'APL-682', 'APL-713', 'APL-894', 'APL-1503', 'APL-1539', 'APL-1439', 'APL-1211', 'APL-1081', 'APL-1149', 'APL-1305', 'APL-1852', 'APL-1535', 'APL-1634', 'APL-1208', 'APL-686', 'APL-694', 'APL-1354', 'APL-1328', 'APL-1275', 'APL-1234', 'APL-678', 'APL-688', 'APL-1252', 'APL-1373', 'APL-1412', 'APL-1530', 'APL-1124', 'APL-1427', 'APL-1204', 'APL-1185', 'APL-1152', 'APL-1086', 'APL-692', 'APL-1127', 'APL-1832', 'APL-1433', 'APL-1107', 'APL-1842', 'APL-1854', 'APL-1270', 'APL-1414', 'APL-666', 'APL-1182', 'APL-1429', 'APL-1342', 'APL-1195', 'APL-707', 'APL-705', 'APL-1156', 'APL-1377', 'APL-1857', 'APL-1165', 'APL-1522', 'APL-974', 'APL-892', 'APL-897', 'APL-983', 'APL-1190', 'APL-1355', 'APL-1300', 'APL-1516', 'APL-1290', 'APL-1096', 'APL-1245', 'APL-712', 'APL-1513', 'APL-1352', 'APL-1855', 'APL-1283', 'APL-1422', 'APL-1314', 'APL-701', 'APL-1207', 'APL-671', 'APL-1379', 'APL-874', 'APL-1099', 'APL-1242', 'APL-1533', 'APL-1485', 'APL-1143', 'APL-1254', 'APL-1417', 'APL-1397', 'APL-1526', 'APL-1908', 'APL-1631', 'APL-1869', 'APL-1222', 'APL-1145', 'APL-1203', 'APL-1505', 'APL-690', 'APL-1078', 'APL-1180', 'APL-1332', 'APL-1287', 'APL-1536', 'APL-683', 'APL-882', 'APL-1189', 'APL-1459', 'APL-1404', 'APL-1316', 'APL-1231', 'APL-900', 'APL-1438', 'APL-1212', 'APL-1230', 'APL-1874', 'APL-669', 'APL-1623', 'APL-965', 'APL-700', 'APL-1349', 'APL-904', 'APL-1249', 'APL-1357', 'APL-698', 'APL-1899', 'APL-1121', 'APL-901', 'APL-1341', 'APL-1497', 'APL-1624', 'APL-665', 'APL-907', 'APL-1110', 'APL-1303', 'APL-1442', 'APL-1280', 'APL-1267', 'APL-1193', 'APL-1339', 'APL-1540', 'APL-1877', 'APL-1160', 'APL-711', 'APL-1129', 'APL-1320', 'APL-1389', 'APL-1310', 'APL-1346', 'APL-1629', 'APL-1542', 'APL-1396', 'APL-1904', 'APL-1494', 'APL-1421', 'APL-1837', 'APL-1262', 'APL-703', 'APL-1138', 'APL-1322', 'APL-1345', 'APL-1859', 'APL-1838', 'APL-1538', 'APL-1163', 'APL-1194', 'APL-1215', 'APL-1170', 'APL-1336', 'APL-1384', 'APL-1449', 'APL-1626', 'APL-1227', 'APL-1199', 'APL-1835', 'APL-1186', 'APL-709', 'APL-1335', 'APL-878', 'APL-1331', 'APL-1839', 'APL-1453', 'APL-890', 'APL-888', 'APL-1862', 'APL-675', 'APL-1089', 'APL-1318', 'APL-696', 'APL-1529', 'APL-1115', 'APL-1424', 'APL-1446', 'APL-1431', 'APL-1537', 'APL-1436', 'APL-1117', 'APL-1434', 'APL-1524', 'APL-1113', 'APL-1531', 'APL-1273'}
OBSERVED_EMPTY_SOURCE_LINES={'**Required source:** `FR-AI-016a`; bounded contribution anchors `AC-FR-AI-016a-001`, `AC-FR-AI-016a-002`, `AC-FR-AI-016a-003`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `FR-AI-016a`; bounded contribution anchors `AC-FR-AI-016a-001`, `AC-FR-AI-016a-002`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `FR-AI-016a`; bounded contribution anchors `AC-FR-AI-016a-001`, `AC-FR-AI-016a-003`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `FR-AI-016a`; bounded contribution anchors `AC-FR-AI-016a-002`, `AC-FR-AI-016a-001`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `FR-AI-016a`; bounded contribution anchors `AC-FR-AI-016a-003`, `AC-FR-AI-016a-001`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `FR-AI-016b`; bounded contribution anchors `AC-FR-AI-016b-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `NFR-08`; bounded contribution anchors `AC-NFR-08-004`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-AD-01`; bounded contribution anchors `AC-US-AD-01-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-AD-02`; bounded contribution anchors `AC-US-AD-02-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-AD-03`; bounded contribution anchors `AC-US-AD-03-001`, `AC-US-AD-03-002`, `AC-US-AD-03-003`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-AD-03`; bounded contribution anchors `AC-US-AD-03-001`, `AC-US-AD-03-002`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-AD-04`; bounded contribution anchors `AC-US-AD-04-001`, `AC-US-AD-04-002`, `AC-US-AD-04-003`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-AD-04`; bounded contribution anchors `AC-US-AD-04-001`, `AC-US-AD-04-002`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-AS-01`; bounded contribution anchors `AC-US-AS-01-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-AS-02`; bounded contribution anchors `AC-US-AS-02-001`, `AC-US-AS-02-002`, `AC-US-AS-02-003`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-AS-02`; bounded contribution anchors `AC-US-AS-02-001`, `AC-US-AS-02-002`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-AS-03`; bounded contribution anchors `AC-US-AS-03-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-CM-02`; bounded contribution anchors `AC-US-CM-02-001`, `AC-US-CM-02-002`, `AC-US-CM-02-003`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-CM-02`; bounded contribution anchors `AC-US-CM-02-001`, `AC-US-CM-02-003`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-CM-02`; bounded contribution anchors `AC-US-CM-02-002`, `AC-US-CM-02-003`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-CM-03`; bounded contribution anchors `AC-US-CM-03-001`, `AC-US-CM-03-002`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-CM-03`; bounded contribution anchors `AC-US-CM-03-001`, `AC-US-CM-03-002`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-CM-04`; bounded contribution anchors `AC-US-CM-04-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-CM-05`; bounded contribution anchors `AC-US-CM-05-001`, `AC-US-CM-05-002`, `AC-US-CM-05-003`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-CM-05`; bounded contribution anchors `AC-US-CM-05-001`, `AC-US-CM-05-002`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-CM-05`; bounded contribution anchors `AC-US-CM-05-001`, `AC-US-CM-05-003`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-CM-05`; bounded contribution anchors `AC-US-CM-05-003`, `AC-US-CM-05-001`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-CM-06`; bounded contribution anchors `AC-US-CM-06-001`, `AC-US-CM-06-002`, `AC-US-CM-06-003`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-CM-06`; bounded contribution anchors `AC-US-CM-06-001`, `AC-US-CM-06-003`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-CM-06`; bounded contribution anchors `AC-US-CM-06-002`, `AC-US-CM-06-003`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-CM-07`; bounded contribution anchors `AC-US-CM-07-001`, `AC-US-CM-07-002`, `AC-US-CM-07-003`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-CM-07`; bounded contribution anchors `AC-US-CM-07-001`, `AC-US-CM-07-002`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-CM-07`; bounded contribution anchors `AC-US-CM-07-003`, `AC-US-CM-07-001`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-CM-08`; bounded contribution anchors `AC-US-CM-08-001`, `AC-US-CM-08-002`, `AC-US-CM-08-003`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-CM-08`; bounded contribution anchors `AC-US-CM-08-002`, `AC-US-CM-08-003`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-CM-09`; bounded contribution anchors `AC-US-CM-09-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-DC-01`; bounded contribution anchors `AC-US-DC-01-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-DC-02`; bounded contribution anchors `AC-US-DC-02-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-DC-03`; bounded contribution anchors `AC-US-DC-03-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-DC-04`; bounded contribution anchors `AC-US-DC-04-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-DP-02`; bounded contribution anchors `AC-US-DP-02-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-DP-03`; bounded contribution anchors `AC-US-DP-03-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-DP-04`; bounded contribution anchors `AC-US-DP-04-001`, `AC-US-DP-04-002`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-DP-04`; bounded contribution anchors `AC-US-DP-04-001`, `AC-US-DP-04-002`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-DP-04`; bounded contribution anchors `AC-US-DP-04-002`, `AC-US-DP-04-001`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-DX-01a`; bounded contribution anchors `AC-US-DX-01a-001`, `AC-US-DX-01a-002`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-DX-01a`; bounded contribution anchors `AC-US-DX-01a-001`, `AC-US-DX-01a-002`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-DX-01a`; bounded contribution anchors `AC-US-DX-01a-002`, `AC-US-DX-01a-001`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-DX-01b`; bounded contribution anchors `AC-US-DX-01b-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-DX-02`; bounded contribution anchors `AC-US-DX-02-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-DX-03`; bounded contribution anchors `AC-US-DX-03-001`, `AC-US-DX-03-002`, `AC-US-DX-03-003`, `AC-US-DX-03-004`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-DX-03`; bounded contribution anchors `AC-US-DX-03-001`, `AC-US-DX-03-002`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-DX-03`; bounded contribution anchors `AC-US-DX-03-002`, `AC-US-DX-03-001`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-DX-03`; bounded contribution anchors `AC-US-DX-03-004`, `AC-US-DX-03-001`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-DX-03`; bounded contribution anchors `AC-US-DX-03-004`, `AC-US-DX-03-002`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-DX-04`; bounded contribution anchors `AC-US-DX-04-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-DX-05`; bounded contribution anchors `AC-US-DX-05-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-FP-01`; bounded contribution anchors `AC-US-FP-01-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-FP-02`; bounded contribution anchors `AC-US-FP-02-001`, `AC-US-FP-02-002`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-FP-02`; bounded contribution anchors `AC-US-FP-02-001`, `AC-US-FP-02-002`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-FP-02`; bounded contribution anchors `AC-US-FP-02-002`, `AC-US-FP-02-001`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-FP-03`; bounded contribution anchors `AC-US-FP-03-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-FP-04`; bounded contribution anchors `AC-US-FP-04-001`, `AC-US-FP-04-002`, `AC-US-FP-04-003`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-FP-04`; bounded contribution anchors `AC-US-FP-04-001`, `AC-US-FP-04-002`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-IM-01`; bounded contribution anchors `AC-US-IM-01-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-IM-02`; bounded contribution anchors `AC-US-IM-02-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-IM-03`; bounded contribution anchors `AC-US-IM-03-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-IM-04`; bounded contribution anchors `AC-US-IM-04-001`, `AC-US-IM-04-002`, `AC-US-IM-04-003`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-IM-04`; bounded contribution anchors `AC-US-IM-04-002`, `AC-US-IM-04-003`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-IM-04`; bounded contribution anchors `AC-US-IM-04-003`, `AC-US-IM-04-001`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-IM-05`; bounded contribution anchors `AC-US-IM-05-001`, `AC-US-IM-05-002`, `AC-US-IM-05-003`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-IM-05`; bounded contribution anchors `AC-US-IM-05-001`, `AC-US-IM-05-002`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-MP-01`; bounded contribution anchors `AC-US-MP-01-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-MP-02`; bounded contribution anchors `AC-US-MP-02-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-MP-03`; bounded contribution anchors `AC-US-MP-03-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-MP-04`; bounded contribution anchors `AC-US-MP-04-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-OP-01`; bounded contribution anchors `AC-US-OP-01-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-OP-02`; bounded contribution anchors `AC-US-OP-02-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-PL-03`; bounded contribution anchors `AC-US-PL-03-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-PT-01`; bounded contribution anchors `AC-US-PT-01-001`, `AC-US-PT-01-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-PT-01`; bounded contribution anchors `AC-US-PT-01-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-PT-02`; bounded contribution anchors `AC-US-PT-02-001`, `AC-US-PT-02-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-PT-02`; bounded contribution anchors `AC-US-PT-02-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-PT-03`; bounded contribution anchors `AC-US-PT-03-001`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-PT-03`; bounded contribution anchors `AC-US-PT-03-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-PT-04`; bounded contribution anchors `AC-US-PT-04-001`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-PT-04`; bounded contribution anchors `AC-US-PT-04-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-PT-05`; bounded contribution anchors `AC-US-PT-05-001`, `AC-US-PT-05-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-PT-05`; bounded contribution anchors `AC-US-PT-05-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-PT-06`; bounded contribution anchors `AC-US-PT-06-001`, `AC-US-PT-06-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-PT-06`; bounded contribution anchors `AC-US-PT-06-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-RT-01`; bounded contribution anchors `AC-US-RT-01-001`, `AC-US-RT-01-003`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-RT-01`; bounded contribution anchors `AC-US-RT-01-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-RT-02`; bounded contribution anchors `AC-US-RT-02-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-RT-03`; bounded contribution anchors `AC-US-RT-03-001`, `AC-US-RT-03-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-RT-03`; bounded contribution anchors `AC-US-RT-03-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-RT-05`; bounded contribution anchors `AC-US-RT-05-001`, `AC-US-RT-05-002`, `AC-US-RT-05-003`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-RT-05`; bounded contribution anchors `AC-US-RT-05-001`, `AC-US-RT-05-002`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-RT-05`; bounded contribution anchors `AC-US-RT-05-002`, `AC-US-RT-05-001`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-VC-01`; bounded contribution anchors `AC-US-VC-01-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-VC-02`; bounded contribution anchors `AC-US-VC-02-001`, `AC-US-VC-02-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-VC-02`; bounded contribution anchors `AC-US-VC-02-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-VC-03`; bounded contribution anchors `AC-US-VC-03-002`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-VC-04`; bounded contribution anchors `AC-US-VC-04-001`, `AC-US-VC-04-002`, `AC-US-VC-04-003`. Proposed explicit verification duty on this existing task; it does not alter the source task core. Original requirement: ': None, '**Required source:** `US-VC-04`; bounded contribution anchors `AC-US-VC-04-001`, `AC-US-VC-04-002`. Proposed nearest source behavior mapping using this bounded task title/scope; owner/engineer confirm during refinement. No acceptance coverage claimed. Original requirement: ': None, '**Required source:** `US-VC-05`; bounded contribution anchors `AC-US-VC-05-001`, `AC-US-VC-05-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None, '**Required source:** `US-VC-05`; bounded contribution anchors `AC-US-VC-05-003`. Exact source scenario label or current plan assertion appears in the unchanged task core. Original requirement: ': None}
VOLATILE_ISSUE={'description','updatedAt'}
VOLATILE_DOCUMENT={'content','updatedAt','updatedBy'}
VOLATILE_PROJECT={'description','updatedAt','resources','resourceCount','milestones'}

def sha(value):
    if isinstance(value,str):value=value.encode('utf-8')
    return hashlib.sha256(value).hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text())

def issue_rows(value):
    if not isinstance(value,dict) or not isinstance(value.get('issues'),list):
        raise ValueError('Issue snapshot must be the actual {issues: [...]} full-issue object.')
    return value['issues']

def document_rows(value):
    # Before capture is a list; the fresh full capture explicitly wraps the
    # same complete records in {documents: [...]}. No content normalization.
    if isinstance(value,list):return value
    if isinstance(value,dict) and set(value)=={'documents'} and isinstance(value['documents'],list):return value['documents']
    raise ValueError('Document snapshot must be a full-record list or the explicit {documents: [...]} object.')

def object_index(rows,key,label,errors):
    if not isinstance(rows,list):
        errors.append({'code':'INVALID_COLLECTION','object':label});return {}
    result={}
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get(key),str) or not row[key]:
            errors.append({'code':'MISSING_ID','object':label});continue
        if row[key] in result:errors.append({'code':'DUPLICATE_ID','object':label,'id':row[key]})
        result[row[key]]=row
    return result

def canonical_metadata(value, excluded=()):
    """Object key order is immaterial; collection order is preserved except sets."""
    out={k:copy.deepcopy(v) for k,v in value.items() if k not in excluded}
    # Labels and relations are set-like native collections; compare every complete
    # member, preserving all relation types and payload values, only sorting order.
    if isinstance(out.get('labels'),list):
        out['labels']=sorted(out['labels'],key=lambda v:json.dumps(v,sort_keys=True))
    if isinstance(out.get('relations'),dict):
        for key,items in out['relations'].items():
            if isinstance(items,list):out['relations'][key]=sorted(items,key=lambda v:json.dumps(v,sort_keys=True))
    return out

def apply_known_transform(text,name):
    if name in {'observed_three_supplement_heading_code_serialization','observed_empty_nfr08_source_label_space','observed_fixed_supplement_heading_code_serialization','observed_exact_empty_source_label_space'}:
        fixed=({line:line[:-1] for line in OBSERVED_EMPTY_SOURCE_LINES} if name=='observed_exact_empty_source_label_space' else FIXED_HEADING_SERIALIZATIONS if name in {'observed_three_supplement_heading_code_serialization','observed_fixed_supplement_heading_code_serialization'} else {EMPTY_NFR08_SOURCE_LINE:EMPTY_NFR08_SOURCE_LINE[:-1]})
        lines=text.splitlines(keepends=True);out=[];fence=None;seen=set()
        for line in lines:
            start=re.match(r'^\s*(`{3,}|~{3,})',line)
            if start:
                token=start[1][0]
                if fence is None:fence=token
                elif fence==token:fence=None
            bare=line.rstrip('\n')
            if fence is None and bare in fixed:
                if bare in seen:raise ValueError('Each exact observed supplement line may occur once only.')
                seen.add(bare);line=fixed[bare]+('\n' if line.endswith('\n') else '')
            out.append(line)
        if name in {'observed_empty_nfr08_source_label_space','observed_exact_empty_source_label_space'} and len(seen)>1:
            raise ValueError('Only one exact required-source empty-label line is allowed per supplement.')
        return ''.join(out)
    if name=='roadmap_exact_four_column_alignment_serialization':
        # One observed new roadmap table delimiter only. Do not generalize
        # alignment removal to arbitrary documents, tables, cells or code.
        lines=text.splitlines(keepends=True);out=[];fence=None;changed=0
        for line in lines:
            start=re.match(r'^\s*(`{3,}|~{3,})',line)
            if start:
                token=start[1][0]
                if fence is None:fence=token
                elif fence==token:fence=None
            if fence is None and line.rstrip('\n')=='| --- | ---: | --- | --- |':
                changed+=1
                line='| -- | -- | -- | -- |'+('\n' if line.endswith('\n') else '')
            out.append(line)
        if changed>1:raise ValueError('The observed roadmap alignment change is limited to one new table delimiter.')
        return ''.join(out)
    if name=='publication_comment_heading_blankline':
        # The declared platform change applies only to this dated publication
        # marker, never original descriptions, arbitrary paragraphs or code.
        lines=text.splitlines(keepends=True);out=[];fence=None
        for index,line in enumerate(lines):
            start=re.match(r'^\s*(`{3,}|~{3,})',line)
            if start:
                token=start[1][0]
                if fence is None:fence=token
                elif fence==token:fence=None
            out.append(line)
            if fence is None and re.fullmatch(r'<!-- imprana:bundle-v4\.2:[^\n>]+:20261011 -->\n',line) and index+1<len(lines) and re.match(r'#{1,6} ',lines[index+1]):out.append('\n')
        return ''.join(out)
    if name=='remove_single_final_lf':
        return text[:-1] if text.endswith('\n') else text
    if name in ONLY_NORMALIZATIONS:
        lines=text.splitlines(keepends=True);out=[];fence=None;blank_count=0;seen_nonblank=False
        for line in lines:
            bare=line.rstrip('\n')
            start=re.match(r'^\s*(`{3,}|~{3,})',bare)
            if start:
                token=start[1][0]
                if fence is None:fence=token
                elif fence==token:fence=None
                out.append(line);blank_count=0;seen_nonblank=True;continue
            if fence is not None:
                out.append(line);continue
            if name=='outside_fence_blankline_collapse':
                if line=='\n':
                    blank_count+=1
                    if blank_count>(1 if seen_nonblank else 2):continue
                else:blank_count=0;seen_nonblank=True
            elif name=='table_separator_three_to_two_dashes' and re.fullmatch(r'\|(?: *--- *\|)+',bare):
                line=bare.replace('---','--')+('\n' if line.endswith('\n') else '')
            elif name=='table_trailing_cell_two_to_one_spaces' and bare.startswith('|') and bare.endswith('|') and '`' not in bare:
                # Only exactly two formatting spaces immediately before a table
                # delimiter; sentence/internal whitespace and three+ spaces stay.
                line=re.sub(r'(?<! )  \|',' |',line)
            elif name=='specific_missing_context_bracket_escape' and bare.startswith('|') and bare.endswith('|') and '`' not in bare:
                line=line.replace('[Missing in original; see proposed clarification]',r'\[Missing in original; see proposed clarification\]')
            elif name=='leading_bold_code_emdash_heading':
                m=re.fullmatch(r'\*\*(`[^`\n]+`) (— [^\n]+)\*\*',bare)
                if m:line=m[1]+' **'+m[2]+'**'+('\n' if line.endswith('\n') else '')
            out.append(line)
        return ''.join(out)
    raise ValueError('Unknown or broad normalization is prohibited: '+str(name))

def permitted_transforms(policy,kind,obj_id):
    matches=[]
    for rule in policy.get('rules',[]):
        if not isinstance(rule,dict) or rule.get('transform') not in ONLY_NORMALIZATIONS:
            raise ValueError('Unsupported normalization policy.')
        if not isinstance(rule.get('evidence'),str) or not rule['evidence'].strip():
            raise ValueError('A declared normalization needs its specific observed platform evidence reference.')
        if rule.get('transform')=='roadmap_exact_four_column_alignment_serialization' and (rule.get('kind')!='documents' or rule.get('ids')!=[ROADMAP_DOCUMENT]):
            raise ValueError('The exact roadmap alignment rule is prohibited outside its one observed document.')
        if rule.get('transform') in {'observed_three_supplement_heading_code_serialization','observed_empty_nfr08_source_label_space','observed_fixed_supplement_heading_code_serialization','observed_exact_empty_source_label_space'}:
            allowed={'observed_three_supplement_heading_code_serialization':OBSERVED_HEADING_IDS,'observed_empty_nfr08_source_label_space':OBSERVED_EMPTY_LABEL_IDS,'observed_fixed_supplement_heading_code_serialization':OBSERVED_FIXED_HEADING_IDS,'observed_exact_empty_source_label_space':OBSERVED_ALL_EMPTY_LABEL_IDS}[rule['transform']]
            ids=rule.get('ids')
            if rule.get('kind')!='issues' or not isinstance(ids,list) or not ids or not set(ids)<=allowed:
                raise ValueError('The fixed observed issue suffix rule is prohibited outside its declared IDs.')
        if rule.get('kind')==kind and obj_id in rule.get('ids',[]):
            matches.append(rule['transform'])
    return list(dict.fromkeys(matches))

def match_appended(before,append,actual,kind,obj_id,policy,errors,normalizations):
    if not all(isinstance(v,str) for v in [before,append,actual]):
        errors.append({'code':'CONTENT_TYPE','kind':kind,'id':obj_id});return False
    if not actual.startswith(before):
        errors.append({'code':'ORIGINAL_PREFIX_CHANGED','kind':kind,'id':obj_id,'before_sha256':sha(before),'actual_sha256':sha(actual)});return False
    expected=before+append
    if actual==expected:return True
    names=permitted_transforms(policy,kind,obj_id)
    # Try only explicitly declared, fixed semantic transformations of the new
    # suffix. No stripping/normalization ever touches the old source prefix.
    # Rich-text emits the complete declared syntax normalization together. Try
    # that exact candidate first, then only its explicit fixed-rule subsets.
    combinations=[tuple(names)] if names else []
    combinations.extend(c for count in range(1,len(names)+1) for c in itertools.combinations(names,count) if c!=tuple(names))
    for combination in combinations:
        transformed=append;changed=[]
        for name in combination:
            new=apply_known_transform(transformed,name)
            if new!=transformed:changed.append(name)
            transformed=new
        if actual==before+transformed:
            normalizations.append({'kind':kind,'id':obj_id,'transforms':changed,'original_prefix_raw_exact':True,'expected_raw_sha256':sha(expected),'observed_sha256':sha(actual),'observed_suffix_sha256':sha(actual[len(before):])})
            return True
    errors.append({'code':'APPEND_CONTENT_MISMATCH','kind':kind,'id':obj_id,'expected_raw_sha256':sha(expected),'observed_sha256':sha(actual)});return False

def compare_metadata(before,after,excluded,kind,obj_id,errors):
    a=canonical_metadata(before,excluded);b=canonical_metadata(after,excluded)
    if a!=b:
        differing=sorted(k for k in set(a)|set(b) if (k in a)!=(k in b) or a.get(k)!=b.get(k))
        errors.append({'code':'METADATA_CHANGED','kind':kind,'id':obj_id,'fields':differing})

def verify(before_issues,after_issues,plan,before_docs,after_docs,before_project,after_project,source_gherkin,policy=None):
    policy=policy or {'rules':[]}
    errors=[];normalizations=[];counts={}
    before=object_index(issue_rows(before_issues),'id','before issues',errors)
    after=object_index(issue_rows(after_issues),'id','after issues',errors)
    planned=object_index(plan.get('issues'),'id','planned issues',errors)
    if len(before)!=EXPECTED_TOTAL or len(after)!=EXPECTED_TOTAL or len(planned)!=EXPECTED_TOTAL:
        errors.append({'code':'ISSUE_COUNT','before':len(before),'after':len(after),'planned':len(planned),'required':EXPECTED_TOTAL})
    if set(before)!=set(after) or set(before)!=set(planned):errors.append({'code':'ISSUE_ID_SET_CHANGED'})
    if plan.get('product')!='Imprana Commons' or plan.get('issue_count')!=EXPECTED_TOTAL:errors.append({'code':'PLAN_SCOPE'})
    seen_canonical=set();uuid_before=set();types={k:0 for k in EXPECTED_COUNTS};all_edges_before=0;all_edges_after=0
    gh_count=0;metadata_absent={k:0 for k in ['estimate','cycle','assignee']}
    for iid,b in before.items():
        if iid not in after or iid not in planned:continue
        a=after[iid];p=planned[iid]
        marker=CANONICAL.match(b.get('description',''))
        if not marker:
            errors.append({'code':'SOURCE_CANONICAL_MARKER','id':iid});continue
        kind,cid=marker.groups();types[kind]+=1
        if cid in seen_canonical:errors.append({'code':'CANONICAL_DUPLICATE','canonical_id':cid})
        seen_canonical.add(cid)
        if b.get('uuid') in uuid_before:errors.append({'code':'UUID_DUPLICATE','id':iid})
        uuid_before.add(b.get('uuid'))
        if p.get('canonical_id')!=cid or p.get('type')!=kind or p.get('uuid')!=b.get('uuid') or a.get('uuid')!=b.get('uuid'):
            errors.append({'code':'IDENTITY_CHANGED','id':iid,'canonical_id':cid})
        if p.get('before_sha256')!=sha(b['description']):errors.append({'code':'PLAN_BEFORE_PIN_MISMATCH','id':iid})
        append=p.get('append')
        if not isinstance(append,str) or not append.strip():
            errors.append({'code':'MISSING_APPEND','id':iid});continue
        if kind=='task':
            markers=TASK_PUBLICATION.findall(append)
            closing=f'<!-- /imprana:task-execution-refinement:{cid}:2026-10-11:v1 -->'
            if markers!=[cid] or append.count(closing)!=1:errors.append({'code':'APPEND_MARKER_SCOPE_OR_DUPLICATION','id':iid})
            if TASK_PUBLICATION.search(b['description']):errors.append({'code':'BEFORE_ALREADY_CONTAINS_NEW_EDITION','id':iid})
        else:
            own_markers=PUBLICATION.findall(append)
            if own_markers!=[(kind,cid)]:errors.append({'code':'APPEND_MARKER_SCOPE_OR_DUPLICATION','id':iid})
            if PUBLICATION.search(b['description']):errors.append({'code':'BEFORE_ALREADY_CONTAINS_NEW_EDITION','id':iid})
        match_appended(b['description'],append,a.get('description'), 'issues',iid,policy,errors,normalizations)
        compare_metadata(b,a,VOLATILE_ISSUE,'issues',iid,errors)
        for field in metadata_absent:
            if field not in b:metadata_absent[field]+=1
        for obj in [b,a]:
            relations=obj.get('relations')
            if not isinstance(relations,dict) or not isinstance(relations.get('blockedBy'),list):errors.append({'code':'RELATION_SNAPSHOT_MISSING','id':iid})
        if kind=='task':
            all_edges_before+=len(b.get('relations',{}).get('blockedBy',[]))
            all_edges_after+=len(a.get('relations',{}).get('blockedBy',[]))
        if kind=='story':
            if cid not in source_gherkin:
                errors.append({'code':'SOURCE_GHERKIN_NOT_AVAILABLE','canonical_id':cid});continue
            source=source_gherkin[cid]
            # Extract only the original fence from the raw source prefix. Repeated
            # Gherkin in a new supplement cannot disguise loss of the original.
            bblocks=re.findall(r'```gherkin\n(.*?)\n```',b['description'],re.S)
            ablocks=re.findall(r'```gherkin\n(.*?)\n```',a.get('description','')[:len(b['description'])],re.S)
            if bblocks!=[source] or ablocks!=[source]:errors.append({'code':'ORIGINAL_GHERKIN_CHANGED','canonical_id':cid})
            gh_count+=len(re.findall(r'^\s*Scenario(?: Outline)?:',source,re.M))
    if types!=EXPECTED_COUNTS:errors.append({'code':'ISSUE_TYPE_COUNTS','actual':types,'required':EXPECTED_COUNTS})
    if all_edges_before!=EXPECTED_TASK_EDGES or all_edges_after!=EXPECTED_TASK_EDGES:errors.append({'code':'TASK_EDGE_COUNT','before':all_edges_before,'after':all_edges_after,'required':EXPECTED_TASK_EDGES})
    if gh_count!=1328:errors.append({'code':'ORIGINAL_SCENARIO_COUNT','actual':gh_count,'required':1328})
    # Specific planned improvements are required by payload, not counted as new
    # source scenarios. Exact appendix read-back above verifies their contents.
    missing_context=set();augmentation=set();ownership=set()
    for p in planned.values():
        text=p.get('append','')
        missing_context.update(re.findall(r'(AC-[A-Za-z0-9-]+-\d{3})`?[^\n]*proposed Given fixture note',text))
        augmentation.update(re.findall(r'(AC-[A-Za-z0-9-]+-\d{3})`?[^\n]*classify existing plan enrichment separately',text))
        ownership.update(re.findall(r'Proposed verification duty on existing `(TASK-[^`]+)`',text))
    if (len(missing_context),len(augmentation),len(ownership))!=(37,7,13):errors.append({'code':'ACTIONABLE_SUPPLEMENT_COUNTS','actual':[len(missing_context),len(augmentation),len(ownership)],'required':[37,7,13]})

    bd=object_index(document_rows(before_docs),'id','before documents',errors);ad=object_index(document_rows(after_docs),'id','after documents',errors)
    pd=object_index(plan.get('documents'),'id','planned documents',errors)
    if len(bd)!=11 or len(pd)!=10 or len(ad)!=12:errors.append({'code':'DOCUMENT_COUNT','before':len(bd),'planned_updates':len(pd),'after':len(ad),'required':[11,10,12]})
    if not set(pd)<set(bd):errors.append({'code':'DOCUMENT_UPDATE_SCOPE'})
    if not set(bd)<=set(ad):errors.append({'code':'EXISTING_DOCUMENT_LOST'})
    protected_docs=set(bd)-set(pd)
    historical_id='37cd9321-6f7d-4df8-973d-557a199de68b'
    if protected_docs!={historical_id}:errors.append({'code':'HISTORICAL_SPLIT_DOCUMENT_SCOPE'})
    for did,b in bd.items():
        if did not in ad:continue
        a=ad[did]
        if did in pd:
            p=pd[did]
            if p.get('before')!=b.get('content') or p.get('title')!=b.get('title'):errors.append({'code':'DOCUMENT_PLAN_SOURCE_MISMATCH','id':did})
            match_appended(b.get('content'),p.get('append'),a.get('content'),'documents',did,policy,errors,normalizations)
            compare_metadata(b,a,VOLATILE_DOCUMENT,'documents',did,errors)
        elif b!=a:
            errors.append({'code':'PROTECTED_HISTORY_DOCUMENT_CHANGED','id':did})
    added=set(ad)-set(bd)
    if len(added)!=1:errors.append({'code':'OVERVIEW_NEW_DOCUMENT_COUNT','actual':len(added)})
    overview_id=next(iter(added)) if len(added)==1 else None
    if overview_id:
        overview=ad[overview_id];wanted=plan.get('overview',{})
        if overview.get('title')!=wanted.get('title'):errors.append({'code':'OVERVIEW_TITLE'})
        match_appended('',wanted.get('content'),overview.get('content'),'overview',overview_id,policy,errors,normalizations)
        if overview.get('archivedAt') is not None:errors.append({'code':'OVERVIEW_ARCHIVED'})

    if not isinstance(before_project,dict) or not isinstance(after_project,dict):
        errors.append({'code':'PROJECT_SNAPSHOT_MISSING'})
    else:
        project_id=before_project.get('uuid')
        match_appended(before_project.get('description'),plan.get('project_append'),after_project.get('description'),'project',project_id,policy,errors,normalizations)
        compare_metadata(before_project,after_project,VOLATILE_PROJECT,'project',project_id,errors)
        bm=object_index(before_project.get('milestones'),'id','before milestones',errors);am=object_index(after_project.get('milestones'),'id','after milestones',errors);pm=object_index(plan.get('milestones'),'id','planned milestones',errors)
        if len(bm)!=5 or set(bm)!=set(am) or set(bm)!=set(pm):errors.append({'code':'MILESTONE_SCOPE_OR_COUNT'})
        for mid,b in bm.items():
            if mid not in am or mid not in pm:continue
            a=am[mid];p=pm[mid]
            if p.get('before')!=b.get('description') or p.get('name')!=b.get('name') or p.get('expected_targetDate')!=b.get('targetDate'):errors.append({'code':'MILESTONE_PLAN_SOURCE_MISMATCH','id':mid})
            match_appended(b.get('description'),p.get('append'),a.get('description'),'milestones',mid,policy,errors,normalizations)
            compare_metadata(b,a,{'description'},'milestones',mid,errors)
        br=object_index(before_project.get('resources'),'id','before project resources',errors);ar=object_index(after_project.get('resources'),'id','after project resources',errors)
        if not set(br)<=set(ar) or set(ar)-set(br)!=({overview_id} if overview_id else set()):errors.append({'code':'PROJECT_RESOURCE_SCOPE'})
        for rid,b in br.items():
            if rid not in ar:continue
            a=ar[rid]
            if rid in pd:
                # Actual fresh native captures project a document's intentional
                # modification timestamp into its resource entry. Permit no
                # arbitrary timestamp waiver: both projections must exactly
                # equal their corresponding complete document capture, and
                # every other resource field remains byte/value exact.
                for label,resource,document in [('before',b,bd.get(rid,{})),('after',a,ad.get(rid,{}))]:
                    if not isinstance(resource.get('updatedAt'),str) or not resource['updatedAt'] or resource['updatedAt']!=document.get('updatedAt'):
                        errors.append({'code':'PROJECT_DOCUMENT_TIMESTAMP_PROJECTION_MISMATCH','id':rid,'capture':label})
                if {k:v for k,v in b.items() if k!='updatedAt'}!={k:v for k,v in a.items() if k!='updatedAt'}:errors.append({'code':'EXISTING_PROJECT_RESOURCE_CHANGED','id':rid})
            elif b!=a:errors.append({'code':'EXISTING_PROJECT_RESOURCE_CHANGED','id':rid})
        if isinstance(before_project.get('resourceCount'),int) and after_project.get('resourceCount')!=before_project['resourceCount']+1:errors.append({'code':'PROJECT_RESOURCE_COUNT'})
    counts={'issues_before':len(before),'issues_after':len(after),'issue_types':types,'original_scenarios':gh_count,'task_blocked_by_edges_before':all_edges_before,'task_blocked_by_edges_after':all_edges_after,'updated_documents':len(pd),'protected_history_documents':len(protected_docs),'new_overview_documents':len(added),'milestones':len(plan.get('milestones',[])),'missing_given_supplements':len(missing_context),'supplementary_assertion_classifications':len(augmentation),'qualification_duty_supplements':len(ownership),'in_review_before':sum(i.get('status')=='In Review' for i in before.values()),'in_review_after':sum(i.get('status')=='In Review' for i in after.values()),'nonmissing_estimates_before':sum('estimate' in i for i in before.values()),'nonmissing_estimates_after':sum('estimate' in i for i in after.values())}
    if counts['in_review_before']!=4 or counts['nonmissing_estimates_before']!=10:errors.append({'code':'SOURCE_WORKFLOW_BASELINE','in_review':counts['in_review_before'],'estimates':counts['nonmissing_estimates_before']})
    return {'result':'PASS' if not errors else 'FAIL','scope':'Offline native read-back content/identity/visible-metadata/relationship preservation. Not application acceptance, test execution, human approval, production readiness or live-provider evidence.','counts':counts,'errors':errors,'declared_platform_normalizations_observed':normalizations,'metadata_scope':{'compared':'Every captured issue field except intentional description/updatedAt; cycle/assignee/estimate presence and any values are preserved. Set-like label/relation ordering may differ; all full members/types/values remain exact.','absent_in_before':metadata_absent,'limitation':'A field omitted by the native full-issue response is not a separately queried backend null; this verifier cannot certify unobserved provider fields.'}}

def default_base():return Path(__file__).resolve().parent.parent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',type=Path,default=default_base())
    parser.add_argument('--repository',type=Path,default=default_base().parents[1]/'work/imprana-framework-refinement-20261011')
    parser.add_argument('--normalization-policy',type=Path)
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent/'PUBLICATION-VERIFICATION-REPORT.json')
    args=parser.parse_args();paths={
       'before_issues':args.base/'native-before/full-issues.json','after_issues':args.base/'native-after/full-issues.json',
       'plan':args.base/'native-publication-plan.json','before_docs':args.base/'native-before/full-documents.json','after_docs':args.base/'native-after/full-documents.json',
       'before_project':args.base/'native-before/project.json','after_project':args.base/'native-after/project.json',
       'source_csv':args.repository/'docs/backlog/backlog.csv'}
    report={'result':'FAIL','scope':'Offline native publication verification','errors':[]}
    try:
        missing=[str(p) for p in paths.values() if not p.is_file()]
        if missing:raise ValueError('Required actual evidence is missing: '+', '.join(missing))
        expected_pins=read_json(Path(__file__).resolve().parent/'EXPECTED-BEFORE-AND-PLAN-PINS.json')
        pin_errors=[]
        for p in expected_pins['files']:
            actual=Path(p['path'])
            if not actual.is_file() or sha(actual.read_bytes())!=p['sha256']:pin_errors.append({'code':'PINNED_BEFORE_OR_PLAN_CHANGED','path':str(actual)})
        with paths['source_csv'].open(newline='') as f:
            gh={r['ID']:r['Acceptance and rejection criteria (Gherkin)'] for r in csv.DictReader(f) if r['Status']!='Split'}
        policy=read_json(args.normalization_policy) if args.normalization_policy else {'rules':[]}
        report=verify(read_json(paths['before_issues']),read_json(paths['after_issues']),read_json(paths['plan']),read_json(paths['before_docs']),read_json(paths['after_docs']),read_json(paths['before_project']),read_json(paths['after_project']),gh,policy)
        protected=read_json(Path(__file__).resolve().parent/'PROTECTED-HISTORY-PINS.json')
        for p in protected['files']:
            actual=args.repository/p['relative_path']
            if not actual.is_file() or sha(actual.read_bytes())!=p['sha256']:pin_errors.append({'code':'PROTECTED_LOCAL_HISTORY_CHANGED','path':str(actual)})
        report['errors'].extend(pin_errors)
        if report['errors']:report['result']='FAIL'
        report['protected_local_history_files']=len(protected['files'])
        report['input_pins']={k:{'path':str(p),'sha256':sha(p.read_bytes())} for k,p in paths.items()}
        if args.normalization_policy:report['normalization_policy_pin']={'path':str(args.normalization_policy),'sha256':sha(args.normalization_policy.read_bytes())}
        report['verifier_sha256']=sha(Path(__file__).read_bytes())
    except Exception as exc:
        report['result']='FAIL';report.setdefault('errors',[]).append({'code':'MISSING_OR_INVALID_EVIDENCE','message':str(exc)})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'result':report['result'],'errors':len(report['errors']),'report':str(args.output)},indent=2))
    return 0 if report['result']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
