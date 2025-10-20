/*
	Copyright 2024-2025 ChipFoundry, a DBA of Umbralogic Technologies LLC.

	Original Copyright 2024 Efabless Corp.
	Author: Efabless Corp. (ip_admin@efabless.com)

	Licensed under the Apache License, Version 2.0 (the "License");
	you may not use this file except in compliance with the License.
	You may obtain a copy of the License at

	    http://www.apache.org/licenses/LICENSE-2.0

	Unless required by applicable law or agreed to in writing, software
	distributed under the License is distributed on an "AS IS" BASIS,
	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
	See the License for the specific language governing permissions and
	limitations under the License.

*/

#include "CF_TMR32.h"

static CF_DRIVER_STATUS set_pwm_action(volatile uint32_t *reg,
                                       uint32_t mask,
                                       uint32_t bit,
                                       uint32_t action) {
	if (action > CF_TMR32_ACTION_MAX_VALUE) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	uint32_t value = *reg;
	value &= ~mask;
	value |= ((action << bit) & mask);
	*reg = value;

	return CF_DRIVER_OK;
}

static CF_DRIVER_STATUS set_cfg_dir(CF_TMR32_TYPE_PTR tmr32, uint32_t dir_bits) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->CFG &= ~CF_TMR32_CFG_REG_DIR_MASK;
	tmr32->CFG |= ((dir_bits << CF_TMR32_CFG_REG_DIR_BIT) & CF_TMR32_CFG_REG_DIR_MASK);
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_setGclkEnable(CF_TMR32_TYPE_PTR tmr32, uint32_t value) {
	if (tmr32 == NULL || value > 1U) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->GCLK = value;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_enable(CF_TMR32_TYPE_PTR tmr32) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->CTRL |= CF_TMR32_CTRL_REG_TE_MASK;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_disable(CF_TMR32_TYPE_PTR tmr32) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->CTRL &= ~CF_TMR32_CTRL_REG_TE_MASK;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_restart(CF_TMR32_TYPE_PTR tmr32) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->CTRL |= CF_TMR32_CTRL_REG_TS_MASK;
	tmr32->CTRL &= ~CF_TMR32_CTRL_REG_TS_MASK;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_PWM0Enable(CF_TMR32_TYPE_PTR tmr32) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->CTRL |= CF_TMR32_CTRL_REG_P0E_MASK;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_PWM1Enable(CF_TMR32_TYPE_PTR tmr32) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->CTRL |= CF_TMR32_CTRL_REG_P1E_MASK;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_PWMDeadtimeEnable(CF_TMR32_TYPE_PTR tmr32) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->CTRL |= CF_TMR32_CTRL_REG_DTE_MASK;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_PWM0Invert(CF_TMR32_TYPE_PTR tmr32) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->CTRL |= CF_TMR32_CTRL_REG_PI0_MASK;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_PWM1Invert(CF_TMR32_TYPE_PTR tmr32) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->CTRL |= CF_TMR32_CTRL_REG_PI1_MASK;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_setUpCount(CF_TMR32_TYPE_PTR tmr32) {
	return set_cfg_dir(tmr32, 0b10U);
}

CF_DRIVER_STATUS CF_TMR32_setDownCount(CF_TMR32_TYPE_PTR tmr32) {
	return set_cfg_dir(tmr32, 0b01U);
}

CF_DRIVER_STATUS CF_TMR32_setUpDownCount(CF_TMR32_TYPE_PTR tmr32) {
	return set_cfg_dir(tmr32, 0b11U);
}

CF_DRIVER_STATUS CF_TMR32_setPeriodic(CF_TMR32_TYPE_PTR tmr32) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->CFG |= CF_TMR32_CFG_REG_P_MASK;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_setOneShot(CF_TMR32_TYPE_PTR tmr32) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->CFG &= ~CF_TMR32_CFG_REG_P_MASK;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_setPWM0MatchingZeroAction(CF_TMR32_TYPE_PTR tmr32, uint32_t action) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	return set_pwm_action(&tmr32->PWM0CFG, CF_TMR32_PWM0CFG_REG_E0_MASK, CF_TMR32_PWM0CFG_REG_E0_BIT, action);
}

CF_DRIVER_STATUS CF_TMR32_setPWM0MatchingCMPXUpCountAction(CF_TMR32_TYPE_PTR tmr32, uint32_t action) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	return set_pwm_action(&tmr32->PWM0CFG, CF_TMR32_PWM0CFG_REG_E1_MASK, CF_TMR32_PWM0CFG_REG_E1_BIT, action);
}

CF_DRIVER_STATUS CF_TMR32_setPWM0MatchingCMPYUpCountAction(CF_TMR32_TYPE_PTR tmr32, uint32_t action) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	return set_pwm_action(&tmr32->PWM0CFG, CF_TMR32_PWM0CFG_REG_E2_MASK, CF_TMR32_PWM0CFG_REG_E2_BIT, action);
}

CF_DRIVER_STATUS CF_TMR32_setPWM0MatchingRELOADAction(CF_TMR32_TYPE_PTR tmr32, uint32_t action) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	return set_pwm_action(&tmr32->PWM0CFG, CF_TMR32_PWM0CFG_REG_E3_MASK, CF_TMR32_PWM0CFG_REG_E3_BIT, action);
}

CF_DRIVER_STATUS CF_TMR32_setPWM0MatchingCMPYDownCountAction(CF_TMR32_TYPE_PTR tmr32, uint32_t action) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	return set_pwm_action(&tmr32->PWM0CFG, CF_TMR32_PWM0CFG_REG_E4_MASK, CF_TMR32_PWM0CFG_REG_E4_BIT, action);
}

CF_DRIVER_STATUS CF_TMR32_setPWM0MatchingCMPXDownCountAction(CF_TMR32_TYPE_PTR tmr32, uint32_t action) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	return set_pwm_action(&tmr32->PWM0CFG, CF_TMR32_PWM0CFG_REG_E5_MASK, CF_TMR32_PWM0CFG_REG_E5_BIT, action);
}

CF_DRIVER_STATUS CF_TMR32_setPWM1MatchingZeroAction(CF_TMR32_TYPE_PTR tmr32, uint32_t action) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	return set_pwm_action(&tmr32->PWM1CFG, CF_TMR32_PWM1CFG_REG_E0_MASK, CF_TMR32_PWM1CFG_REG_E0_BIT, action);
}

CF_DRIVER_STATUS CF_TMR32_setPWM1MatchingCMPXUpCountingAction(CF_TMR32_TYPE_PTR tmr32, uint32_t action) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	return set_pwm_action(&tmr32->PWM1CFG, CF_TMR32_PWM1CFG_REG_E1_MASK, CF_TMR32_PWM1CFG_REG_E1_BIT, action);
}

CF_DRIVER_STATUS CF_TMR32_setPWM1MatchingCMPYUpCountingAction(CF_TMR32_TYPE_PTR tmr32, uint32_t action) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	return set_pwm_action(&tmr32->PWM1CFG, CF_TMR32_PWM1CFG_REG_E2_MASK, CF_TMR32_PWM1CFG_REG_E2_BIT, action);
}

CF_DRIVER_STATUS CF_TMR32_setPWM1MatchingRELOADAction(CF_TMR32_TYPE_PTR tmr32, uint32_t action) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	return set_pwm_action(&tmr32->PWM1CFG, CF_TMR32_PWM1CFG_REG_E3_MASK, CF_TMR32_PWM1CFG_REG_E3_BIT, action);
}

CF_DRIVER_STATUS CF_TMR32_setPWM1MatchingCMPYDownCountAction(CF_TMR32_TYPE_PTR tmr32, uint32_t action) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	return set_pwm_action(&tmr32->PWM1CFG, CF_TMR32_PWM1CFG_REG_E4_MASK, CF_TMR32_PWM1CFG_REG_E4_BIT, action);
}

CF_DRIVER_STATUS CF_TMR32_setPWM1MatchingCMPXDownCountAction(CF_TMR32_TYPE_PTR tmr32, uint32_t action) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	return set_pwm_action(&tmr32->PWM1CFG, CF_TMR32_PWM1CFG_REG_E5_MASK, CF_TMR32_PWM1CFG_REG_E5_BIT, action);
}

CF_DRIVER_STATUS CF_TMR32_setRELOAD(CF_TMR32_TYPE_PTR tmr32, uint32_t value) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->RELOAD = value;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_setCMPX(CF_TMR32_TYPE_PTR tmr32, uint32_t value) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->CMPX = value;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_getCMPX(CF_TMR32_TYPE_PTR tmr32, uint32_t *value) {
	if (tmr32 == NULL || value == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	*value = tmr32->CMPX;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_getCMPY(CF_TMR32_TYPE_PTR tmr32, uint32_t *value) {
	if (tmr32 == NULL || value == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	*value = tmr32->CMPY;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_setCMPY(CF_TMR32_TYPE_PTR tmr32, uint32_t value) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->CMPY = value;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_getTMR(CF_TMR32_TYPE_PTR tmr32, uint32_t *tmr_value) {
	if (tmr32 == NULL || tmr_value == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	*tmr_value = tmr32->TMR;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_setPWMDeadtime(CF_TMR32_TYPE_PTR tmr32, uint32_t value) {
	if (tmr32 == NULL || value > CF_TMR32_PWMDT_MAX_VALUE) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->PWMDT = value;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_setPR(CF_TMR32_TYPE_PTR tmr32, uint32_t value) {
	if (tmr32 == NULL || value > CF_TMR32_PR_MAX_VALUE) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->PR = value;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_getRIS(CF_TMR32_TYPE_PTR tmr32, uint32_t *ris_value) {
	if (tmr32 == NULL || ris_value == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	*ris_value = tmr32->RIS;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_getMIS(CF_TMR32_TYPE_PTR tmr32, uint32_t *mis_value) {
	if (tmr32 == NULL || mis_value == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	*mis_value = tmr32->MIS;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_setIM(CF_TMR32_TYPE_PTR tmr32, uint32_t mask) {
	if (tmr32 == NULL || mask > CF_TMR32_IM_MAX_VALUE) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->IM = mask;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_getIM(CF_TMR32_TYPE_PTR tmr32, uint32_t *im_value) {
	if (tmr32 == NULL || im_value == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	*im_value = tmr32->IM;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_setICR(CF_TMR32_TYPE_PTR tmr32, uint32_t mask) {
	if (tmr32 == NULL || mask > CF_TMR32_ICR_MAX_VALUE) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->IC = mask;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_isTimout(CF_TMR32_TYPE_PTR tmr32, bool *timeout_status) {
	if (tmr32 == NULL || timeout_status == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	uint32_t ris_value = 0U;
	CF_DRIVER_STATUS status = CF_TMR32_getRIS(tmr32, &ris_value);
	if (status != CF_DRIVER_OK) {
		return status;
	}

	*timeout_status = ((ris_value & CF_TMR32_TO_FLAG) != 0U);
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_isCMPXMatch(CF_TMR32_TYPE_PTR tmr32, bool *match_status) {
	if (tmr32 == NULL || match_status == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	uint32_t ris_value = 0U;
	CF_DRIVER_STATUS status = CF_TMR32_getRIS(tmr32, &ris_value);
	if (status != CF_DRIVER_OK) {
		return status;
	}

	*match_status = ((ris_value & CF_TMR32_MX_FLAG) != 0U);
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_isCMPYMatch(CF_TMR32_TYPE_PTR tmr32, bool *match_status) {
	if (tmr32 == NULL || match_status == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	uint32_t ris_value = 0U;
	CF_DRIVER_STATUS status = CF_TMR32_getRIS(tmr32, &ris_value);
	if (status != CF_DRIVER_OK) {
		return status;
	}

	*match_status = ((ris_value & CF_TMR32_MY_FLAG) != 0U);
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_clearTimoutFlag(CF_TMR32_TYPE_PTR tmr32) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->IC = CF_TMR32_TO_FLAG;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_clearCMPXMatchFlag(CF_TMR32_TYPE_PTR tmr32) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->IC = CF_TMR32_MX_FLAG;
	return CF_DRIVER_OK;
}

CF_DRIVER_STATUS CF_TMR32_clearCMPYMatchFlag(CF_TMR32_TYPE_PTR tmr32) {
	if (tmr32 == NULL) {
		return CF_DRIVER_ERROR_PARAMETER;
	}

	tmr32->IC = CF_TMR32_MY_FLAG;
	return CF_DRIVER_OK;
}

void CF_TMR32_configureExamplePWM(CF_TMR32_TYPE_PTR tmr32)
{
	if (tmr32 == NULL) {
		return;
	}

	const uint32_t reload = 1000U;
	const uint32_t cmpx = 250U;
	const uint32_t cmpy = 750U;

	CF_TMR32_setGclkEnable(tmr32, 1U);
	CF_TMR32_setPR(tmr32, 0U);
	CF_TMR32_setRELOAD(tmr32, reload);
	CF_TMR32_setCMPX(tmr32, cmpx);
	CF_TMR32_setCMPY(tmr32, cmpy);
	CF_TMR32_setUpCount(tmr32);
	CF_TMR32_setPeriodic(tmr32);
	CF_TMR32_setPWM0MatchingZeroAction(tmr32, CF_TMR32_ACTION_NONE);
	CF_TMR32_setPWM0MatchingCMPXUpCountAction(tmr32, CF_TMR32_ACTION_LOW);
	CF_TMR32_setPWM0MatchingCMPYUpCountAction(tmr32, CF_TMR32_ACTION_LOW);
	CF_TMR32_setPWM0MatchingRELOADAction(tmr32, CF_TMR32_ACTION_HIGH);
	CF_TMR32_setPWM0MatchingCMPYDownCountAction(tmr32, CF_TMR32_ACTION_HIGH);
	CF_TMR32_setPWM0MatchingCMPXDownCountAction(tmr32, CF_TMR32_ACTION_NONE);
	CF_TMR32_setPWM1MatchingZeroAction(tmr32, CF_TMR32_ACTION_NONE);
	CF_TMR32_setPWM1MatchingCMPXUpCountingAction(tmr32, CF_TMR32_ACTION_LOW);
	CF_TMR32_setPWM1MatchingCMPYUpCountingAction(tmr32, CF_TMR32_ACTION_LOW);
	CF_TMR32_setPWM1MatchingRELOADAction(tmr32, CF_TMR32_ACTION_HIGH);
	CF_TMR32_setPWM1MatchingCMPYDownCountAction(tmr32, CF_TMR32_ACTION_HIGH);
	CF_TMR32_setPWM1MatchingCMPXDownCountAction(tmr32, CF_TMR32_ACTION_NONE);
	CF_TMR32_PWM0Enable(tmr32);
	CF_TMR32_PWM1Enable(tmr32);
	CF_TMR32_enable(tmr32);
	CF_TMR32_restart(tmr32);
}
