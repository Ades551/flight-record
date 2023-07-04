import { Navbar, Nav, Container } from "react-bootstrap";

const NavBar = () => {
    return (
        <>
            <Navbar collapseOnSelect sticky="top" expand="lg" bg="dark" variant="dark">
                <Container className="min-vw-100">
                    <Navbar.Brand href="/">FlightRecord</Navbar.Brand>
                    <Nav className="me-auto">
                        <Nav.Link href="/records">Records</Nav.Link>
                    </Nav>
                </Container>
            </Navbar>
        </>
    );
}

export default NavBar;
