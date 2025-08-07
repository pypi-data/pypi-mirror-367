#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* precon.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscksp.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcreset_ PCRESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcreset_ pcreset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcdestroy_ PCDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcdestroy_ pcdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgetdiagonalscale_ PCGETDIAGONALSCALE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgetdiagonalscale_ pcgetdiagonalscale
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcsetdiagonalscale_ PCSETDIAGONALSCALE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcsetdiagonalscale_ pcsetdiagonalscale
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcdiagonalscaleleft_ PCDIAGONALSCALELEFT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcdiagonalscaleleft_ pcdiagonalscaleleft
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcdiagonalscaleright_ PCDIAGONALSCALERIGHT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcdiagonalscaleright_ pcdiagonalscaleright
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcsetuseamat_ PCSETUSEAMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcsetuseamat_ pcsetuseamat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcseterroriffailure_ PCSETERRORIFFAILURE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcseterroriffailure_ pcseterroriffailure
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgetuseamat_ PCGETUSEAMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgetuseamat_ pcgetuseamat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcsetkspnestlevel_ PCSETKSPNESTLEVEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcsetkspnestlevel_ pcsetkspnestlevel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgetkspnestlevel_ PCGETKSPNESTLEVEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgetkspnestlevel_ pcgetkspnestlevel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pccreate_ PCCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pccreate_ pccreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcapply_ PCAPPLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcapply_ pcapply
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmatapply_ PCMATAPPLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmatapply_ pcmatapply
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcapplysymmetricleft_ PCAPPLYSYMMETRICLEFT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcapplysymmetricleft_ pcapplysymmetricleft
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcapplysymmetricright_ PCAPPLYSYMMETRICRIGHT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcapplysymmetricright_ pcapplysymmetricright
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcapplytranspose_ PCAPPLYTRANSPOSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcapplytranspose_ pcapplytranspose
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcapplytransposeexists_ PCAPPLYTRANSPOSEEXISTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcapplytransposeexists_ pcapplytransposeexists
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcapplybaorab_ PCAPPLYBAORAB
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcapplybaorab_ pcapplybaorab
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcapplybaorabtranspose_ PCAPPLYBAORABTRANSPOSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcapplybaorabtranspose_ pcapplybaorabtranspose
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcapplyrichardsonexists_ PCAPPLYRICHARDSONEXISTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcapplyrichardsonexists_ pcapplyrichardsonexists
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcapplyrichardson_ PCAPPLYRICHARDSON
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcapplyrichardson_ pcapplyrichardson
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcsetfailedreason_ PCSETFAILEDREASON
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcsetfailedreason_ pcsetfailedreason
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgetfailedreason_ PCGETFAILEDREASON
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgetfailedreason_ pcgetfailedreason
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcreducefailedreason_ PCREDUCEFAILEDREASON
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcreducefailedreason_ pcreducefailedreason
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcsetup_ PCSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcsetup_ pcsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcsetuponblocks_ PCSETUPONBLOCKS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcsetuponblocks_ pcsetuponblocks
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcsetoperators_ PCSETOPERATORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcsetoperators_ pcsetoperators
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcsetreusepreconditioner_ PCSETREUSEPRECONDITIONER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcsetreusepreconditioner_ pcsetreusepreconditioner
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgetreusepreconditioner_ PCGETREUSEPRECONDITIONER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgetreusepreconditioner_ pcgetreusepreconditioner
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgetoperators_ PCGETOPERATORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgetoperators_ pcgetoperators
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgetoperatorsset_ PCGETOPERATORSSET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgetoperatorsset_ pcgetoperatorsset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorgetmatrix_ PCFACTORGETMATRIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorgetmatrix_ pcfactorgetmatrix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcsetoptionsprefix_ PCSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcsetoptionsprefix_ pcsetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcappendoptionsprefix_ PCAPPENDOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcappendoptionsprefix_ pcappendoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgetoptionsprefix_ PCGETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgetoptionsprefix_ pcgetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcpresolve_ PCPRESOLVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcpresolve_ pcpresolve
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcpostsolve_ PCPOSTSOLVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcpostsolve_ pcpostsolve
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcload_ PCLOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcload_ pcload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcviewfromoptions_ PCVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcviewfromoptions_ pcviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcview_ PCVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcview_ pcview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pccomputeoperator_ PCCOMPUTEOPERATOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pccomputeoperator_ pccomputeoperator
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcsetcoordinates_ PCSETCOORDINATES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcsetcoordinates_ pcsetcoordinates
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgetinterpolations_ PCGETINTERPOLATIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgetinterpolations_ pcgetinterpolations
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgetcoarseoperators_ PCGETCOARSEOPERATORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgetcoarseoperators_ pcgetcoarseoperators
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pcreset_(PC pc, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCReset(
	(PC)PetscToPointer((pc) ));
}
PETSC_EXTERN void  pcdestroy_(PC *pc, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(pc);
 PetscBool pc_null = !*(void**) pc ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(pc);
*ierr = PCDestroy(pc);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! pc_null && !*(void**) pc) * (void **) pc = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(pc);
 }
PETSC_EXTERN void  pcgetdiagonalscale_(PC pc,PetscBool *flag, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGetDiagonalScale(
	(PC)PetscToPointer((pc) ),flag);
}
PETSC_EXTERN void  pcsetdiagonalscale_(PC pc,Vec s, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(s);
*ierr = PCSetDiagonalScale(
	(PC)PetscToPointer((pc) ),
	(Vec)PetscToPointer((s) ));
}
PETSC_EXTERN void  pcdiagonalscaleleft_(PC pc,Vec in,Vec out, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(in);
CHKFORTRANNULLOBJECT(out);
*ierr = PCDiagonalScaleLeft(
	(PC)PetscToPointer((pc) ),
	(Vec)PetscToPointer((in) ),
	(Vec)PetscToPointer((out) ));
}
PETSC_EXTERN void  pcdiagonalscaleright_(PC pc,Vec in,Vec out, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(in);
CHKFORTRANNULLOBJECT(out);
*ierr = PCDiagonalScaleRight(
	(PC)PetscToPointer((pc) ),
	(Vec)PetscToPointer((in) ),
	(Vec)PetscToPointer((out) ));
}
PETSC_EXTERN void  pcsetuseamat_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCSetUseAmat(
	(PC)PetscToPointer((pc) ),*flg);
}
PETSC_EXTERN void  pcseterroriffailure_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCSetErrorIfFailure(
	(PC)PetscToPointer((pc) ),*flg);
}
PETSC_EXTERN void  pcgetuseamat_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGetUseAmat(
	(PC)PetscToPointer((pc) ),flg);
}
PETSC_EXTERN void  pcsetkspnestlevel_(PC pc,PetscInt *level, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCSetKSPNestLevel(
	(PC)PetscToPointer((pc) ),*level);
}
PETSC_EXTERN void  pcgetkspnestlevel_(PC pc,PetscInt *level, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLINTEGER(level);
*ierr = PCGetKSPNestLevel(
	(PC)PetscToPointer((pc) ),level);
}
PETSC_EXTERN void  pccreate_(MPI_Fint * comm,PC *newpc, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(newpc);
 PetscBool newpc_null = !*(void**) newpc ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newpc);
*ierr = PCCreate(
	MPI_Comm_f2c(*(comm)),newpc);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newpc_null && !*(void**) newpc) * (void **) newpc = (void *)-2;
}
PETSC_EXTERN void  pcapply_(PC pc,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = PCApply(
	(PC)PetscToPointer((pc) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  pcmatapply_(PC pc,Mat X,Mat Y, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(Y);
*ierr = PCMatApply(
	(PC)PetscToPointer((pc) ),
	(Mat)PetscToPointer((X) ),
	(Mat)PetscToPointer((Y) ));
}
PETSC_EXTERN void  pcapplysymmetricleft_(PC pc,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = PCApplySymmetricLeft(
	(PC)PetscToPointer((pc) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  pcapplysymmetricright_(PC pc,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = PCApplySymmetricRight(
	(PC)PetscToPointer((pc) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  pcapplytranspose_(PC pc,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = PCApplyTranspose(
	(PC)PetscToPointer((pc) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  pcapplytransposeexists_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCApplyTransposeExists(
	(PC)PetscToPointer((pc) ),flg);
}
PETSC_EXTERN void  pcapplybaorab_(PC pc,PCSide *side,Vec x,Vec y,Vec work, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
CHKFORTRANNULLOBJECT(work);
*ierr = PCApplyBAorAB(
	(PC)PetscToPointer((pc) ),*side,
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ),
	(Vec)PetscToPointer((work) ));
}
PETSC_EXTERN void  pcapplybaorabtranspose_(PC pc,PCSide *side,Vec x,Vec y,Vec work, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
CHKFORTRANNULLOBJECT(work);
*ierr = PCApplyBAorABTranspose(
	(PC)PetscToPointer((pc) ),*side,
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ),
	(Vec)PetscToPointer((work) ));
}
PETSC_EXTERN void  pcapplyrichardsonexists_(PC pc,PetscBool *exists, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCApplyRichardsonExists(
	(PC)PetscToPointer((pc) ),exists);
}
PETSC_EXTERN void  pcapplyrichardson_(PC pc,Vec b,Vec y,Vec w,PetscReal *rtol,PetscReal *abstol,PetscReal *dtol,PetscInt *its,PetscBool *guesszero,PetscInt *outits,PCRichardsonConvergedReason *reason, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(b);
CHKFORTRANNULLOBJECT(y);
CHKFORTRANNULLOBJECT(w);
CHKFORTRANNULLINTEGER(outits);
*ierr = PCApplyRichardson(
	(PC)PetscToPointer((pc) ),
	(Vec)PetscToPointer((b) ),
	(Vec)PetscToPointer((y) ),
	(Vec)PetscToPointer((w) ),*rtol,*abstol,*dtol,*its,*guesszero,outits,reason);
}
PETSC_EXTERN void  pcsetfailedreason_(PC pc,PCFailedReason *reason, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCSetFailedReason(
	(PC)PetscToPointer((pc) ),*reason);
}
PETSC_EXTERN void  pcgetfailedreason_(PC pc,PCFailedReason *reason, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGetFailedReason(
	(PC)PetscToPointer((pc) ),reason);
}
PETSC_EXTERN void  pcreducefailedreason_(PC pc, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCReduceFailedReason(
	(PC)PetscToPointer((pc) ));
}
PETSC_EXTERN void  pcsetup_(PC pc, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCSetUp(
	(PC)PetscToPointer((pc) ));
}
PETSC_EXTERN void  pcsetuponblocks_(PC pc, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCSetUpOnBlocks(
	(PC)PetscToPointer((pc) ));
}
PETSC_EXTERN void  pcsetoperators_(PC pc,Mat Amat,Mat Pmat, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(Amat);
CHKFORTRANNULLOBJECT(Pmat);
*ierr = PCSetOperators(
	(PC)PetscToPointer((pc) ),
	(Mat)PetscToPointer((Amat) ),
	(Mat)PetscToPointer((Pmat) ));
}
PETSC_EXTERN void  pcsetreusepreconditioner_(PC pc,PetscBool *flag, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCSetReusePreconditioner(
	(PC)PetscToPointer((pc) ),*flag);
}
PETSC_EXTERN void  pcgetreusepreconditioner_(PC pc,PetscBool *flag, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGetReusePreconditioner(
	(PC)PetscToPointer((pc) ),flag);
}
PETSC_EXTERN void  pcgetoperators_(PC pc,Mat *Amat,Mat *Pmat, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool Amat_null = !*(void**) Amat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Amat);
PetscBool Pmat_null = !*(void**) Pmat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Pmat);
*ierr = PCGetOperators(
	(PC)PetscToPointer((pc) ),Amat,Pmat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Amat_null && !*(void**) Amat) * (void **) Amat = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Pmat_null && !*(void**) Pmat) * (void **) Pmat = (void *)-2;
}
PETSC_EXTERN void  pcgetoperatorsset_(PC pc,PetscBool *mat,PetscBool *pmat, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGetOperatorsSet(
	(PC)PetscToPointer((pc) ),mat,pmat);
}
PETSC_EXTERN void  pcfactorgetmatrix_(PC pc,Mat *mat, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = PCFactorGetMatrix(
	(PC)PetscToPointer((pc) ),mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  pcsetoptionsprefix_(PC pc, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = PCSetOptionsPrefix(
	(PC)PetscToPointer((pc) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  pcappendoptionsprefix_(PC pc, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = PCAppendOptionsPrefix(
	(PC)PetscToPointer((pc) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  pcgetoptionsprefix_(PC pc, char *prefix, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGetOptionsPrefix(
	(PC)PetscToPointer((pc) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for prefix */
*ierr = PetscStrncpy(prefix, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, prefix, cl0);
}
PETSC_EXTERN void  pcpresolve_(PC pc,KSP ksp, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(ksp);
*ierr = PCPreSolve(
	(PC)PetscToPointer((pc) ),
	(KSP)PetscToPointer((ksp) ));
}
PETSC_EXTERN void  pcpostsolve_(PC pc,KSP ksp, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(ksp);
*ierr = PCPostSolve(
	(PC)PetscToPointer((pc) ),
	(KSP)PetscToPointer((ksp) ));
}
PETSC_EXTERN void  pcload_(PC newdm,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(newdm);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PCLoad(
	(PC)PetscToPointer((newdm) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  pcviewfromoptions_(PC A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PCViewFromOptions(
	(PC)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  pcview_(PC pc,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PCView(
	(PC)PetscToPointer((pc) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  pccomputeoperator_(PC pc,char *mattype,Mat *mat, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
/* insert Fortran-to-C conversion for mattype */
  FIXCHAR(mattype,cl0,_cltmp0);
*ierr = PCComputeOperator(
	(PC)PetscToPointer((pc) ),_cltmp0,mat);
  FREECHAR(mattype,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  pcsetcoordinates_(PC pc,PetscInt *dim,PetscInt *nloc,PetscReal coords[], int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLREAL(coords);
*ierr = PCSetCoordinates(
	(PC)PetscToPointer((pc) ),*dim,*nloc,coords);
}
PETSC_EXTERN void  pcgetinterpolations_(PC pc,PetscInt *num_levels,Mat *interpolations[], int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLINTEGER(num_levels);
CHKFORTRANNULLOBJECT(interpolations);
*ierr = PCGetInterpolations(
	(PC)PetscToPointer((pc) ),num_levels,interpolations);
}
PETSC_EXTERN void  pcgetcoarseoperators_(PC pc,PetscInt *num_levels,Mat *coarseOperators[], int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLINTEGER(num_levels);
CHKFORTRANNULLOBJECT(coarseOperators);
*ierr = PCGetCoarseOperators(
	(PC)PetscToPointer((pc) ),num_levels,coarseOperators);
}
#if defined(__cplusplus)
}
#endif
