import pytest
import json
from datetime import datetime
from services.reconnaissance.amass_adapter import AmassAdapter
from services.reconnaissance.sn1per_adapter import Sn1perAdapter
from services.reconnaissance.service import ReconnaissanceService
from agents.passive_recon.schema import (
    PassiveReconInput,
    PassiveReconOutput,
    SubdomainFinding,
    ASNInfo
)


class TestAmassAdapter:
    """Test Amass passive reconnaissance."""

    def test_amass_available(self):
        """Check if Amass is installed."""
        amass = AmassAdapter()
        # Can be skipped if Amass not installed
        assert isinstance(amass.is_available(), bool)

    def test_amass_enum_passive(self):
        """Test passive subdomain enumeration."""
        amass = AmassAdapter()
        if not amass.is_available():
            pytest.skip("Amass not installed")

        results = amass.enum_passive("example.com")
        assert isinstance(results, list)
        if results:
            assert "host" in results[0]
            assert "source" in results[0]

    def test_amass_asn_discovery(self):
        """Test ASN discovery."""
        amass = AmassAdapter()
        if not amass.is_available():
            pytest.skip("Amass not installed")

        results = amass.asn_discovery("example.com")
        assert isinstance(results, list)
        if results:
            assert "asn" in results[0]
            assert "org" in results[0]

    def test_amass_dns_records(self):
        """Test DNS record discovery."""
        amass = AmassAdapter()
        if not amass.is_available():
            pytest.skip("Amass not installed")

        results = amass.dns_records("example.com")
        assert isinstance(results, list)


class TestSn1perAdapter:
    """Test Sn1per reconnaissance framework."""

    def test_sn1per_available(self):
        """Check if Sn1per is installed."""
        sn1per = Sn1perAdapter()
        assert isinstance(sn1per.is_available(), bool)

    def test_sn1per_scan_light(self):
        """Test lightweight Sn1per scan."""
        sn1per = Sn1perAdapter()
        if not sn1per.is_available():
            pytest.skip("Sn1per not installed")

        results = sn1per.scan_light("example.com")
        assert isinstance(results, list)
        if results:
            assert "source" in results[0]
            assert "sn1per" in results[0]["source"]

    def test_sn1per_extract_intelligence(self):
        """Test WHOIS/DNS extraction."""
        sn1per = Sn1perAdapter()
        if not sn1per.is_available():
            pytest.skip("Sn1per not installed")

        intel = sn1per.extract_intelligence("example.com")
        assert isinstance(intel, dict)
        assert "source" in intel or len(intel) == 0


class TestReconnaissanceService:
    """Test integrated reconnaissance service."""

    def test_service_initialization(self):
        """Test service can be instantiated."""
        service = ReconnaissanceService(active_probing=False)
        assert service is not None
        assert service.active_probing is False

    def test_passive_recon_premium(self):
        """Test comprehensive passive recon."""
        service = ReconnaissanceService(active_probing=False)

        # This should work even if tools aren't installed
        results = service.passive_recon_premium("example.com")

        assert "domain" in results
        assert results["domain"] == "example.com"
        assert "subdomains" in results
        assert "asn_info" in results
        assert "dns_records" in results
        assert "techniques" in results

    def test_passive_recon_data_structure(self):
        """Test return data structure."""
        service = ReconnaissanceService()
        results = service.passive_recon_premium("example.com")

        required_keys = [
            "domain",
            "subdomains",
            "asn_info",
            "dns_records",
            "all_hosts",
            "techniques"
        ]

        for key in required_keys:
            assert key in results, f"Missing key: {key}"


class TestPassiveReconSchema:
    """Test data schema validation."""

    def test_passive_recon_input(self):
        """Test input schema."""
        inp = PassiveReconInput(
            domain="example.com",
            run_id="test-123"
        )
        assert inp.domain == "example.com"
        assert inp.run_id == "test-123"
        assert inp.include_asn is True
        assert inp.deep_scan is False

    def test_passive_recon_output(self):
        """Test output schema."""
        output = PassiveReconOutput(
            run_id="test-123",
            domain="example.com",
            completed_at="2024-01-01T00:00:00Z"
        )
        assert output.run_id == "test-123"
        assert output.domain == "example.com"
        assert output.total_subdomains == 0

    def test_subdomain_finding(self):
        """Test subdomain finding schema."""
        finding = SubdomainFinding(
            host="sub.example.com",
            sources=["amass", "sn1per"],
            confidence=0.95
        )
        assert finding.host == "sub.example.com"
        assert len(finding.sources) == 2
        assert finding.confidence == 0.95

    def test_asn_info(self):
        """Test ASN info schema."""
        asn = ASNInfo(
            asn="AS12345",
            org="Example Corp",
            cidr_blocks=["192.0.2.0/24"]
        )
        assert asn.asn == "AS12345"
        assert asn.org == "Example Corp"
        assert len(asn.cidr_blocks) == 1


class TestPassiveReconIntegration:
    """Integration tests for passive reconnaissance."""

    def test_end_to_end_passive_recon(self):
        """Test complete passive recon flow."""
        from agents.passive_recon.agent import run_passive_recon
        import uuid

        inp = PassiveReconInput(
            domain="example.com",
            run_id=str(uuid.uuid4())
        )

        # Should not crash even if tools aren't installed
        result = run_passive_recon(inp)

        assert isinstance(result, PassiveReconOutput)
        assert result.run_id == inp.run_id
        assert result.domain == inp.domain
        assert isinstance(result.completed_at, str)

    def test_deep_scan_option(self):
        """Test deep scan (stealth mode)."""
        from agents.passive_recon.agent import run_passive_recon
        import uuid

        inp = PassiveReconInput(
            domain="example.com",
            run_id=str(uuid.uuid4()),
            deep_scan=True
        )

        result = run_passive_recon(inp)
        assert isinstance(result, PassiveReconOutput)

    def test_results_consolidation(self):
        """Test that results from multiple sources are consolidated."""
        service = ReconnaissanceService()
        results = service.passive_recon_premium("example.com")

        # Should have both Amass and Sn1per results
        assert "amass" in results["subdomains"]
        assert "sn1per" in results["subdomains"]

        # All hosts should be deduplicated
        all_unique = len(set(results["all_hosts"]))
        assert all_unique == len(results["all_hosts"])


class TestDataQuality:
    """Test data quality and validation."""

    def test_no_duplicates_in_results(self):
        """Ensure no duplicate subdomains."""
        service = ReconnaissanceService()
        results = service.passive_recon_premium("example.com")

        hosts = results["all_hosts"]
        assert len(hosts) == len(set(hosts))

    def test_all_required_fields_present(self):
        """Test all required fields are present."""
        from agents.passive_recon.agent import run_passive_recon
        import uuid

        result = run_passive_recon(PassiveReconInput(
            domain="example.com",
            run_id=str(uuid.uuid4())
        ))

        required_fields = [
            "run_id",
            "domain",
            "completed_at",
            "techniques_used",
            "data_sources"
        ]

        for field in required_fields:
            assert hasattr(result, field)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
