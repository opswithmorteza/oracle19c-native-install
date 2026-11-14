"""Static profile contract tests. Never connects to or installs a database."""
import pathlib
import unittest
import yaml

ROOT = pathlib.Path(__file__).parent

class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.inventory = yaml.safe_load((ROOT / 'inventory-19c.example.yml').read_text())
        self.v = self.inventory['oracle19c']['vars']
        self.plays = yaml.safe_load((ROOT / 'install-19c.yml').read_text())

    def test_opt_in_and_secret_boundaries(self):
        for key in ('oracle19c_install_approved', 'oracle19c_license_confirmed', 'oracle19c_ru_reviewed'):
            self.assertIs(self.v[key], False)
        self.assertNotIn('default_dbpass', self.v)

    def test_pinned_dependency_and_real_playbooks(self):
        req = yaml.safe_load((ROOT / 'requirements-19c.yml').read_text())
        self.assertEqual(req['collections'][0]['version'], '97e0255a8cb917e4fa30c257bd8565a699331f06')
        self.assertEqual([p['ansible.builtin.import_playbook'].split('.')[-1] for p in self.plays if 'ansible.builtin.import_playbook' in p], ['os', 'swdb', 'manage_db'])
        for play in self.plays:
            if 'ansible.builtin.import_playbook' in play:
                self.assertEqual(play['vars']['hostgroup'], 'oracle19c')

    def test_preserve_host_protections_and_disks(self):
        for key in ('disable_selinux', 'disable_firewall', 'configure_host_disks', 'firewall_open_listener_ports', 'configure_oracle_sudo'):
            self.assertIs(self.v[key], False)
        self.assertEqual(self.v['host_fs_layout'], [])
        address = self.v['oracle_listeners_config']['LISTENER']['address'][0]
        self.assertEqual(address['host'], '127.0.0.1')

    def test_only_19c_and_matching_database_references(self):
        self.assertEqual(self.v['db_homes_config']['db19']['version'], '19.3.0.0')
        self.assertTrue(self.v['oracle19c_ru'].startswith('19.'))
        homes = self.v['db_homes_config']
        for item in self.v['oracle_databases'] + self.v['oracle_pdbs'] + self.v['db_homes_installed']:
            self.assertIn(item['home'], homes)
        self.assertEqual(self.v['oracle_pdbs'][0]['cdb'], self.v['oracle_databases'][0]['oracle_db_name'])

    def test_guards_precede_mutating_roles(self):
        tasks = self.plays[0]['tasks']
        self.assertEqual(self.plays[0]['hosts'], 'oracle19c')
        self.assertTrue(self.plays[0]['any_errors_fatal'])
        self.assertTrue(any(t.get('ansible.builtin.stat', {}).get('checksum_algorithm') == 'sha256' for t in tasks))
        self.assertTrue(any(t.get('no_log') for t in tasks))
        self.assertIn('/etc/oraInst.loc', str(tasks))

if __name__ == '__main__':
    unittest.main(verbosity=2)
