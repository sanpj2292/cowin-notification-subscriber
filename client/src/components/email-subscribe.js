import React, { useRef, useState, useEffect } from 'react';
import { Container, Grid, TextField, FormControlLabel, Radio, RadioGroup,
MenuItem, Select, FormControl, InputLabel, Button, Box, Paper, CardMedia, Card, CardContent, CardActions, Backdrop, CircularProgress, IconButton, Snackbar, FormLabel } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import CloseIcon from '@material-ui/icons/Close';

const useStyles = makeStyles(theme => ({
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
    },
    backdrop: {
        zIndex: theme.zIndex.drawer + 1,
        color: '#fff',
    },
}));

const EmailSubscribe = props => {
    const classes = useStyles();
    const [backdrop, setBackdrop] = useState(false);
    const [searchType, setSearchType] = useState('');
    const [minAge, setMinAge] = useState('0');
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
        setMinAge('0');
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
    const handleMinAgeChange = (e) => {
        setMinAge(e.target.value);
    }

    useEffect(() => {
        setBackdrop(true);
        fetch('/api/v2/states', {method: 'GET'})
        .then(res => res.json())
        .then(res => {
            setStates(res.states);
        })
        .catch(e => {
            console.error(e);
            setMessage({
                open: true,
                msg: 'Exception occurred, please try to refresh page after sometime'
            });
        })
        .finally(() => {
            setBackdrop(false);
        });
    }, []);


    useEffect(() => {
        // Load districts
        if (state) {
            setBackdrop(true);
            fetch(`/api/v2/districts/${state}`, {
                method: "GET"
            }).then(res => res.json())
            .then(res => {
                setDistricts(res.districts);
            })
            .catch(e => {
                console.error(e);
                setMessage({
                    open: true,
                    msg: 'Exception occurred, please try to refresh page after sometime'
                });
            })
            .finally(() => {
                setBackdrop(false);
            });
        }
    }, [state]);

    const onSubscribeClick = async () => {
        try {
            setBackdrop(true);
            let body = {
                email,
                state_id: state,
                district_id: district,
                min_age: Number(minAge)
            };
            let url = '/api/v2/subscribe';
            if (searchType === "PINCD") {
                body = pincode.split(',').map(p => {
                    if (p.length !== 6) {
                        throw new Error('Invalid Pincode, cannot proceed with Save');
                    }
                    return {
                        email,
                        search_type: searchType,
                        pincode: Number(p.trim()),
                        min_age: Number(minAge)
                    };
                });
                url = '/api/v2/pincode/subscribe';
            }
            const resp = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(body)
            }).then(res => res.json());
            let msg = "";
            if (!resp.isSubscriptionSuccess) {
                msg = 'Could not complete the request, try again after sometime'
            } else {
                msg = "You've been subscribed, Check your emails for updates"
            }
            setMessage({
                open: true,
                msg
            });
            resetComponentState();
        } catch (error) {
            console.error(error);
            setMessage({
                open: true,
                msg: 'Some error occurred, please try after sometime'
            });
            throw error;
        } finally {
            setBackdrop(false);
        }
    }

    const [message, setMessage] = useState({
        open: false,
        msg: ''
    });
    const handleMessageClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setMessage({open: false, msg: ''});
    }

    return (
    <Box className={classes.box}>
        <Snackbar
            anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
            }}
            open={message.open}
            autoHideDuration={6000}
            onClose={handleMessageClose}
            message={message.msg}
            action={
            <>
                <IconButton aria-label="close" color="inherit"
                className={classes.close} onClick={handleMessageClose}
                >
                    <CloseIcon />
                </IconButton>
            </>
            }
        />
        <Backdrop className={classes.backdrop} open={backdrop}>
            <CircularProgress color="inherit" />
        </Backdrop>
        <Card style={{width: '30vw', }}>
            {/* <CardMedia image={'3d-corona-vaccine.jpg'} className={classes.media} title="Corona Vaccine"/> */}
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
                                <FormLabel component="menu">Minimum Age to get Vaccinated</FormLabel>
                                <RadioGroup aria-label="age" name="age" value={minAge} onChange={handleMinAgeChange}>
                                    <Grid direction='row'>
                                        <FormControlLabel value="18" control={<Radio />} label="18" />
                                        <FormControlLabel value="45" control={<Radio />} label="45" />
                                        <FormControlLabel value="0" control={<Radio />} label="None" />
                                    </Grid>
                                </RadioGroup>
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