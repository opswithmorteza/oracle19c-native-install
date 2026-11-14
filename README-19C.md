# Oracle 19c Native Installation Profile

Maintained by **Morteza Rajabi** as a focused extension of [oravirt/ansible-oracle](https://github.com/oravirt/ansible-oracle). Original upstream authors, copyright notices and MIT license are retained. This profile does not redistribute or relicense Oracle Database.

## What it does

Installs Oracle Database **directly on a clean Oracle Linux 8 x86_64 host**, using the pinned upstream Ansible roles: OS preparation → Oracle software installation → Listener → ORCLCDB container database → APPPDB → verification. No Docker, Kubernetes, VM creation or disk partitioning is performed by this profile.

**Status: installation candidate, not production-certified.** Oracle 19c is a long-term support release, not a guarantee of zero bugs. This profile requires operator-approved, already patched 19c gold-image media and SHA-256 verification. Its explicit example target is **19.32.0.0.0**; this is not asserted to be the latest or universally recommended RU. Select the RU certified for your OS, application and support entitlement. The upstream `version: 19.3.0.0` selects the 19c installer template, not the desired patch level.

## Prerequisites

- Controller: Linux or WSL2, Python 3.11–3.13, Git and `ansible-core==2.19.4` in an isolated virtual environment.
- One fresh Oracle Linux 8 x86_64 host, reachable by SSH, with a sudo-capable operator. Other OS versions and Windows database hosts are outside this profile.
- At least 8 GB RAM, 8 GB swap, prepared `/u01` and `/u02` directories with **80 GiB free on each checked path**. This is a conservative profile threshold, not Oracle's universal minimum. If both paths share storage, budget for the combined workload and growth.
- Working hostname resolution, time synchronisation and access to approved OS package repositories. Firewall and SELinux remain enabled. The default listener binds to loopback; use an SSH tunnel for local testing.
- Obtain a licensed 19c **RU-patched gold image** from Oracle/My Oracle Support or an authorised internal process. A plain `LINUX.X64_193000_db_home.zip` is not the patched gold image required here. Place the reviewed image at `/u01/sw/db_home_19.32.zip`, readable by the Oracle installation user after OS preparation. Ensure all parent directories are traversable. Verify that the ZIP contains a complete Oracle home, not a patch-only ZIP.
- Obtain its SHA-256 through a trusted, independent source; calculating a digest of an untrusted download does not establish authenticity.

## Prepare and run

Run from this repository root on the controller:

```bash
python3 -m venv .venv19c
. .venv19c/bin/activate
python -m pip install ansible-core==2.19.4 PyYAML==6.0.3
ansible-galaxy collection install -r requirements-19c.yml -p .collections19c
export ANSIBLE_COLLECTIONS_PATH="$PWD/.collections19c"
cp inventory-19c.example.yml inventory-19c.local.yml
ansible-vault create secrets-19c.local.yml
```

In the Vault editor set a strong, unique lab database password:

```yaml
default_dbpass: YOUR_PRIVATE_PASSWORD_AT_LEAST_16_CHARACTERS
```

The simple profile uses the upstream fallback for database accounts; design separate per-account secrets before production. Do not publish plaintext secrets, vault passwords or encrypted vault files containing real infrastructure details. Review how upstream roles handle response files, logs, command arguments and staging artifacts; Vault protects stored controller input, not every runtime artifact.

Edit the local inventory: host address, SSH user, gold-image path, trusted digest and approved RU. After reviewing the scope and license, set the three `oracle19c_*_approved`/confirmation flags to true (`oracle19c_install_approved`, `oracle19c_license_confirmed`, `oracle19c_ru_reviewed`).

```bash
python test_19c_profile.py
ansible-playbook -i inventory-19c.local.yml install-19c.yml --syntax-check
ansible-playbook -i inventory-19c.local.yml install-19c.yml --list-hosts
ansible-playbook -i inventory-19c.local.yml install-19c.yml \
  --ask-become-pass --ask-vault-pass -e @secrets-19c.local.yml
```

Review the exact target in `--list-hosts` before installation. Do not use skipped tags, prerequisite bypasses, `--start-at-task` or overrides to circumvent the guard. Ansible check mode does not simulate OUI or DBCA and cannot prove installation success.

## Boundaries and verification

- Guard rejects existing `/etc/oraInst.loc`, Grid Infrastructure metadata or the target home. This is a **fresh-install** entry point, intentionally not a rerunnable repair or patching tool. Interrupted runs require log review and a clean test host; do not delete a real Oracle inventory to pass the guard.
- OS roles install packages and change Oracle-related limits/sysctl/hugepage configuration. Review changes and any reboot requirements. Storage layout is operator-managed. No generic rollback or automated uninstall is offered.
- After creation, SQL*Plus checks the reported RU and open APPPDB, and prints SQL patch registry status. Review `opatch lsinventory`, `DBA_REGISTRY_SQLPATCH`, DBCA/OUI logs, listener services and PDB save state. Resolve failed/missing SQL patch application before acceptance. Use Oracle's procedure for the selected RU, not an invented patch ID.
- This conservative **isolated development** example uses NOARCHIVELOG. It is not a production backup design. Before real workloads, design ARCHIVELOG, RMAN backups, FRA capacity, deletion policies, monitoring, restore tests, access control, TLS and application-specific sizing. Changing ARCHIVELOG requires an approved database procedure.
- Do not enable optional Enterprise Edition features without entitlement. `control_management_pack_access=NONE` is included but is not a complete licensing assessment.
- No Oracle installation has been executed as part of preparing this repository. Static/configuration tests and syntax checks are distinct from an end-to-end deployment test. Never label this profile as bug-free or certified without evidence from your target environment.

## فارسی

این پروفایل نصب مستقیم 19c روی Oracle Linux 8 است. فایل نصب وصله‌شده و مجاز اوراکل را خودت تأمین می‌کنی، تنظیمات ماشین و checksum را مشخص می‌کنی و رمز را در Ansible Vault قرار می‌دهی. سپس Ansible پیش‌نیازها، نرم‌افزار، لیسنر، CDB و PDB را آماده می‌کند. نمونه برای محیط توسعهٔ ایزوله است؛ نصب کامل روی سرور واقعی هنوز آزمایش نشده و عنوان «تمام باگ‌ها حل شده» برای آن صحیح نیست.

## Sources and pinned baseline

- Upstream commit: `97e0255a8cb917e4fa30c257bd8565a699331f06` (MIT), retained in `requirements-19c.yml`.
- [Oracle 19c installation guide](https://docs.oracle.com/en/database/oracle/oracle-database/19/ladbi/)
- [Oracle response-file workflow](https://docs.oracle.com/en/database/oracle/oracle-database/19/ladbi/response-files.html)
- [Oracle support lifecycle](https://www.oracle.com/assets/lsp-tech-chart-069290.pdf)

Profile additions © 2026 Morteza Rajabi, MIT under the existing repository license. Upstream implementation remains credited to its original contributors.
