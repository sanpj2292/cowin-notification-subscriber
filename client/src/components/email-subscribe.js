import React, { useRef, useState, useEffect } from 'react';
import { Container, Grid, TextField, FormControlLabel, Radio, RadioGroup,
MenuItem, Select, FormControl, InputLabel, Button, Box, Paper, CardMedia, Card, CardContent, CardActions } from '@material-ui/core';
import { makeStyles } from "@material-ui/styles";

const useStyles = makeStyles({
    formControl: {
        minWidth: 120,
        width: '95%'
    },
    paper: {
        width: '30vw', 
        height: '50vh', 
        paddingTop: 16, 
        paddingBottom: 16
    },
    stateSelect: {
        paddingBottom: 8,
        paddingTop: 16,
    },
    box: { 
        display: 'flex', 
        height: '90vh',
        width: '100vw', 
        justifyContent: 'center', 
        alignItems: 'center'
    },
    media: {
        objectFit: 'contain',
        width: '54%',
        height: '29vh',
        backgroundSize: 'cover',
        marginTop: '16px',
        marginLeft: '23%'
    }
});

const EmailSubscribe = props => {
    const classes = useStyles();
    const emailRef = useRef('');
    const [searchType, setSearchType] = useState('');
    const handleSearchTypeChange = e => {
        setSearchType(e.target.value);
    }

    const resetComponentState = () => {
        setEmail('');
        setSearchType();
        setState('')
        setDistrict('');
        setDistricts('');
        setPincode('');
    }

    const [districts, setDistricts] = useState([]);
    const [states, setStates] = useState([]);
    const [pincode, setPincode] = useState('');
    
    const [state, setState] = useState('');
    const handleStateChange = e => {
        setState(e.target.value);
    }
    const [email, setEmail] = useState('');
    const onEmailChange = e => {
        setEmail(e.target.value);
    }
    const [district, setDistrict] = useState('');
    const handleDistrictChange = e => {
        setDistrict(e.target.value);
    }

    const handlePincodeChange = (e) => {
        setPincode(e.target.value);
    }

    useEffect(() => {
        fetch('/v2/states', {method: 'GET'})
        .then(res => res.json())
        .then(res => {
            setStates(res.states);
        });
    }, []);


    useEffect(() => {
        // Load districts
        if (state) {
            fetch(`/v2/districts/${state}`, {
                method: "GET"
            }).then(res => res.json())
            .then(res => {
                setDistricts(res.districts);
            });
        }
    }, [state]);

    const onSubscribeClick = async () => {
        try {
            let body = {
                email,
                state_id: state,
                district_id: district
            };
            let url = '/v2/subscribe';
            if (searchType === "PINCD") {
                body = pincode.split(',').map(p => {
                    if (p.length !== 6) {
                        throw new Error('Invalid Pincode, cannot proceed with Save');
                    }
                    return {
                        email,
                        search_type: searchType,
                        pincode: Number(p.trim()),
                    };
                });
                url = '/v2/pincode/subscribe';
            }
            const resp = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(body)
            }).then(res => res.json())
            console.log(resp);
            resetComponentState();
        } catch (error) {
            console.error(error);
            throw error;
        }
    }

    console.log(process.env.PUBLIC_URL);
    return (
    <Box className={classes.box}>
        <Card style={{width: '30vw', }}>
            <CardMedia image={'3d-corona-vaccine.jpg'} className={classes.media} title="Corona Vaccine"/>
            <CardContent>
                <Grid container justify='center' alignItems='center' direction='row' >
                    <Container>
                        <Grid container direction='column'>
                            <Grid item>
                                <FormControl variant="outlined" className={`${classes.formControl}`}>
                                    <TextField 
                                        id="full-width-email"
                                        label="Email"
                                        placeholder="abc@example.com"
                                        fullWidth
                                        margin="normal"
                                        InputLabelProps={{
                                            shrink: true,
                                        }}
                                        variant="outlined"
                                        type='email'
                                        value={email}
                                        onChange={onEmailChange}
                                    />
                                </FormControl>
                            </Grid>
                            <Grid item>
                                <RadioGroup aria-label="quiz" name="quiz" value={searchType} onChange={handleSearchTypeChange}>
                                    <Grid direction='row'>
                                        <FormControlLabel value="PINCD" control={<Radio />} label="Pincode" />
                                        <FormControlLabel value="STDIS" control={<Radio />} label="District" />
                                    </Grid>
                                </RadioGroup>
                            </Grid>
                            {searchType === 'STDIS' && <Grid item className={classes.stateSelect}>
                                <FormControl variant="outlined" className={`${classes.formControl}`}>
                                    <InputLabel id="state-label">State</InputLabel>
                                    <Select
                                        labelId="state-label"
                                        id="state-select-outlined"
                                        value={state}
                                        onChange={handleStateChange}
                                        label="State"
                                    >
                                        {
                                            states.map(state => (
                                                <MenuItem value={state.state_id}>{state.state_name}</MenuItem>
                                            ))
                                        }
                                    </Select>
                                </FormControl>
                            </Grid>
                            }
                            {searchType === 'STDIS' && state && districts.length > 0 && <Grid item >
                                <FormControl variant="outlined" className={`${classes.formControl}`}>
                                    <InputLabel id="district-label">District</InputLabel>
                                    <Select
                                        labelId="district-label"
                                        id="district-select-outlined"
                                        value={district}
                                        onChange={handleDistrictChange}
                                        label="District"
                                    >
                                        {districts.map(dis => (
                                            <MenuItem value={dis.district_id}>{dis.district_name}</MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            </Grid>
                            }
                            {searchType === 'PINCD' && <Grid item className={classes.stateSelect}>
                                <FormControl variant="outlined" className={`${classes.formControl}`}>
                                    <TextField 
                                        id="full-width-pincode"
                                        label="Pincode"
                                        placeholder="500028,500008,600042"
                                        fullWidth
                                        margin="normal"
                                        InputLabelProps={{
                                            shrink: true,
                                        }}
                                        variant="outlined"
                                        type='text'
                                        value={pincode}
                                        onChange={handlePincodeChange}
                                    />
                                </FormControl>
                            </Grid>
                            }
                        </Grid>
                    </Container>
                </Grid>
            </CardContent>
            <CardActions>
                <Grid container item justify='flex-end' alignContent='center' style={{ marginTop: '11%' }}>
                    <Button variant='contained' color='primary' onClick={onSubscribeClick}>
                        Subscribe
                    </Button>
                </Grid>

            </CardActions>
        </Card>
        {/* <Paper variant="outlined" className={classes.paper}> */}
            {/* <div>
                Subscribe to email updates whenever a slot is available
            </div> */}
        {/* </Paper> */}
    </Box>
    )
}

export default EmailSubscribe;